from decimal import Decimal,InvalidOperation
from ....models import money
from ....storage import digest
from ....tax import TaxRecord
from ...errors import IntegrationError,reject
from .partner import remote_id


def dec(value):
    if not isinstance(value,(str,int,Decimal)) or isinstance(value,bool):raise ValueError('Non-decimal remote amount')
    number=Decimal(value)
    if not number.is_finite() or abs(number)>Decimal('1000000000000'):raise ValueError('Invalid remote amount')
    return number


def invoice(snapshot,server,connection_id):
    move=snapshot.get('move',{});lines=snapshot.get('lines',[]);warnings=[];facts=[]
    if remote_id(move.get('company_id'))!=server.odoo_company_id:reject('scope_violation','Factura ajena a la compañía vinculada',502)
    if type(move.get('id'))!=int or move['id']<=0:reject('invalid_response','Identidad remota inválida',502)
    try:
        kind=move['move_type'];state=move['state']
        if kind not in ('out_invoice','in_invoice','out_refund','in_refund'):raise ValueError('Unsupported move type')
        if state not in ('draft','posted'):raise ValueError('Cancelled or unsupported state')
        if move.get('currency')!='EUR':raise ValueError('Foreign currency requires dedicated mapping')
        if move.get('cash_basis') or move.get('fiscal_position_id'):raise ValueError('Special fiscal context requires review')
        if not move.get('invoice_date'):raise ValueError('Missing operation date')
        if len(lines)>1000:raise ValueError('Too many lines')
        products=[l for l in lines if l.get('display_type')=='product']
        if any(l.get('display_type') not in ('product','line_note','line_section','line_subsection') for l in lines):raise ValueError('Unsupported technical line')
        base=sum((dec(l['price_subtotal']) for l in products),Decimal(0))
        total=sum((dec(l['price_total']) for l in products),Decimal(0))
        if money(base)!=money(dec(move['amount_untaxed'])) or money(total)!=money(dec(move['amount_total'])) or money(total-base)!=money(dec(move['amount_tax'])):
            raise ValueError('Invoice totals do not reconcile')
        sign=Decimal(-1) if kind in ('out_refund','in_refund') else Decimal(1)
        for line in products:
            if remote_id(line.get('company_id'))!=server.odoo_company_id or remote_id(line.get('move_id'))!=move['id']:raise ValueError('Line company or invoice differs')
            lid=line['id']
            if type(lid)!=int or lid<=0:raise ValueError('Line id invalid')
            taxes=line.get('taxes',[]);tax_kind='other';rate=None
            if len(taxes)>1:raise ValueError('Compound/withholding taxes require dedicated mapping')
            b=dec(line['price_subtotal']);t=dec(line['price_total'])-b
            if taxes:
                tax=taxes[0]
                if remote_id(tax.get('company_id'))!=server.odoo_company_id:raise ValueError('Tax company differs')
                expected=server.tax_mappings.get(str(tax['id']))
                if expected:
                    expected_use='sale' if kind.startswith('out_') else 'purchase'
                    if tax.get('amount_type')!='percent' or tax.get('price_include') or tax.get('children_tax_ids') or tax.get('type_tax_use')!=expected_use:raise ValueError('Unverified tax configuration')
                    if expected.get('tax_kind') not in ('iva','igic','ipsi') or dec(expected['rate'])!=dec(tax['amount']):raise ValueError('Configured tax mapping differs')
                    if expected.get('tax_kind')=='iva' and server.tenant_id=='':raise ValueError('Missing tenant')
                    if money(b*dec(tax['amount'])/100)!=money(t):raise ValueError('Tax rounding differs')
                    tax_kind=expected['tax_kind'];rate=str(dec(tax['amount']))
                else:warnings.append('Impuesto sin correspondencia fiscal aprobada; no se infiere por porcentaje.')
            elif t!=0:raise ValueError('Tax amount without tax configuration')
            fact=TaxRecord(external_id=f'odoo:{connection_id}:account.move.line:{lid}:{digest(snapshot)[:20]}',operation_date=move['invoice_date'],kind='income' if kind.startswith('out_') else 'expense',description=str(line.get('name') or 'Línea Odoo')[:1000],counterparty=str(move.get('partner_name') or '')[:200],tax_kind=tax_kind,base_amount=money(b*sign),tax_amount=money(t*sign),withholding_amount='0.00',category='other',vat_treatment='other',tax_rate=rate,deductible_tax_amount=None,deductible_irpf_amount=None,classification_notes='Origen Odoo; pendientes justificante, confirmación de fecha fiscal y clasificación humana.')
            facts.append({'remote_line_id':lid,'record':fact.model_dump(mode='json')})
        if not facts:raise ValueError('No economic product lines')
        if state=='draft':warnings.append('Factura ERP en borrador: no acredita factura emitida ni devengo fiscal.')
        if sign<0:warnings.append('Abono: importes negativos no admitidos por los motores fiscales comunes iniciales.')
        warnings.append('No se infiere deducibilidad, fecha fiscal ni elegibilidad para 303/130.')
        return {'blocked':False,'warnings':sorted(set(warnings)),'facts':facts,'move_id':move['id'],'state':state,'write_date':move.get('write_date')}
    except (ValueError,KeyError,TypeError,InvalidOperation):
        return {'blocked':True,'warnings':['Factura no asignable de forma inequívoca: revisar moneda, fechas, composición fiscal, líneas y conciliación.'],'facts':[],'move_id':move.get('id'),'state':move.get('state'),'write_date':move.get('write_date')}
