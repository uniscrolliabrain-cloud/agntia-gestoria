"""Deterministic, deliberately bounded AEAT 2026 calculation engines."""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator
from .models import Model, money
from .storage import digest
from .territories import territorial_profile

D=Decimal
ZERO=D('0')
RULE_VERSION='aeat-common-2026-v1'
SOURCES={
 '303':'https://sede.agenciatributaria.gob.es/Sede/todas-gestiones/impuestos-tasas/iva/modelo-303-iva-autoliquidacion_/instrucciones-2026/instrucciones-02-12-2t-4t-2026.html',
 '130':'https://sede.agenciatributaria.gob.es/Sede/impuestos-tasas/impuesto-sobre-renta-personas-fisicas/modelo-130-irpf______esionales-estimacion-directa-fraccionado_/instrucciones.html',
}

class Calculation(Model):
    model: Literal['303','130']
    year: Literal[2026]
    period: Literal['1T','2T','3T','4T']
    regime: Literal['iva_general_domestic','irpf_direct_normal']
    confirmed_standard_scope: bool
    # Acknowledges user-confirmed eligibility, completeness and absence of excluded situations.
    # Never inferred from an LLM output or a company's domicile alone.
    prior_vat_credit: D=Field(default=ZERO,ge=0,le=1000000000000,decimal_places=2)
    apply_prior_vat_credit: bool=True
    prior_130_positive_box07_sum: D=Field(default=ZERO,ge=0,le=1000000000000,decimal_places=2)
    prior_130_unused_negative: D=Field(default=ZERO,ge=0,le=1000000000000,decimal_places=2)
    previous_year_net_activity_income: D|None=Field(default=None,ge=-1000000000000,le=1000000000000,decimal_places=2)

    @model_validator(mode='after')
    def scope(self):
        if not self.confirmed_standard_scope:raise ValueError('Confirma el ámbito y la integridad de los datos antes de calcular')
        if self.model=='303' and self.regime!='iva_general_domestic':raise ValueError('Régimen incompatible con el modelo 303')
        if self.model=='130' and (self.regime!='irpf_direct_normal' or self.previous_year_net_activity_income is None):raise ValueError('El 130 requiere estimación directa normal y rendimiento neto del año anterior')
        if self.model=='303' and (self.prior_130_positive_box07_sum or self.prior_130_unused_negative or self.previous_year_net_activity_income is not None):raise ValueError('Hay parámetros de IRPF en un cálculo de IVA')
        if self.model=='130' and self.prior_vat_credit:raise ValueError('Hay compensación de IVA en un cálculo de IRPF')
        if self.period=='1T' and (self.prior_130_positive_box07_sum or self.prior_130_unused_negative):raise ValueError('El primer trimestre no tiene pagos ni negativos anteriores del mismo ejercicio')
        return self


def fail(message):raise ValueError(message)


def calculate(company,all_records,request):
    profile=territorial_profile(company)
    if company['tax_territory']!='common' or any(t!='common' for t in profile['declared_operation_territories']) or any(any(a!='aeat' for a in v) for v in profile['tax_administrations'].values()):
        fail('Este motor admite exclusivamente tributación estatal común, sin repartos ni regímenes territoriales especiales')
    if request.model=='130' and company['legal_form']!='autonomo':fail('El 130 requiere contribuyente persona física')
    facts=company.get('facts',{})
    if request.model=='130' and facts.get('irpf_payment_model','unknown')!='130':fail('Confirma en el perfil que procede el modelo 130')
    if request.model=='303' and (facts.get('vat_return_required') is not True or facts.get('vat_periodicity')!='quarterly' or facts.get('vat_status')!='liable'):
        fail('El motor 303 requiere perfil sujeto, declaración obligatoria confirmada y periodicidad trimestral')
    if facts.get('uses_sii') is True:fail('El perfil SII no está cubierto por este motor inicial')
    quarter=int(request.period[0]);start=date(request.year,1 if request.model=='130' else (quarter-1)*3+1,1)
    end=date(request.year+1,1,1) if quarter==4 else date(request.year,quarter*3+1,1)
    selected=sorted([r for r in all_records if r['status']!='void' and start<=date.fromisoformat(r['operation_date'])<end],key=lambda r:r['id'])
    if not selected:fail('No hay registros; el motor no deduce ausencia de actividad de una base vacía')
    if any(r['status']!='reviewed' for r in selected):fail('Todos los registros del período deben estar revisados por owner/reviewer')
    excluded=[]
    for r in selected:
        non_vat_expense=request.model=='303' and r['kind']=='expense' and r['tax_kind']=='none' and D(r['tax_amount'])==0 and r.get('vat_treatment')=='exempt' and r.get('deductible_tax_amount') is not None and D(r['deductible_tax_amount'])==0
        if non_vat_expense and r.get('category')=='ordinary' and r.get('document_ids') and D(r['base_amount'])>=0 and D(r['withholding_amount'])>=0:
            excluded.append({'id':r['id'],'reason':'Gasto corriente sin IVA, clasificado y revisado, sin cuota deducible; no se traslada al 303.'})
            continue
        if r['kind'] not in ('income','expense') or r.get('vat_treatment')!='domestic_current' or r.get('category')!='ordinary':
            fail('Hay ajustes, operaciones especiales o registros sin clasificación admitida; no se omiten silenciosamente')
        if min(D(r[k]) for k in ('base_amount','tax_amount','withholding_amount'))<0:fail('Rectificaciones con importes negativos requieren otro motor')
        if not r.get('document_ids'):fail('Cada registro necesita al menos un documento de soporte')
        if request.model=='303' and (r['tax_kind']!='iva' or r.get('tax_rate') is None or D(r['tax_rate']) not in (D('4'),D('10'),D('21'))):
            fail('El 303 inicial admite solo IVA interior corriente al 4, 10 o 21 por ciento')
        if request.model=='303' and money(D(r['base_amount'])*D(r['tax_rate'])/100)!=D(r['tax_amount']):
            fail('La cuota no coincide con el tipo y base del registro; revisar redondeo o desglosar las operaciones')
        if request.model=='303' and r['kind']=='expense' and r.get('deductible_tax_amount') is not None and D(r['deductible_tax_amount'])!=D(r['tax_amount']):fail('El 303 inicial admite solo cuotas interiores corrientes íntegramente deducibles; deducciones parciales requieren otro motor')
        if r['kind']=='expense' and r.get('deductible_tax_amount' if request.model=='303' else 'deductible_irpf_amount') is None:
            fail('Falta un importe deducible explícito en un gasto')
    incoming=[r for r in selected if r['kind']=='income'];expenses=[r for r in selected if r['kind']=='expense' and (request.model!='303' or r['tax_kind']=='iva')]
    boxes={};trace=[]
    def put(box,value,formula):
        boxes[box]=str(money(value));trace.append({'box':box,'formula':formula,'value':boxes[box]})
    def total(rows,field):return sum((D(r[field]) for r in rows),ZERO)
    if request.model=='303':
        for rate,basebox,ratebox,taxbox in [('4','01','02','03'),('10','04','05','06'),('21','07','08','09')]:
            rows=[r for r in incoming if D(r['tax_rate'])==D(rate)]
            put(basebox,total(rows,'base_amount'),'Suma de bases de ventas al '+rate+'%')
            put(ratebox,D(rate),'Tipo declarado y comprobado')
            put(taxbox,total(rows,'tax_amount'),'Suma de cuotas de las operaciones; redondeo por registro')
        put('27',total(incoming,'tax_amount'),'03 + 06 + 09; resto de cuotas devengadas fuera de ámbito')
        put('28',total(expenses,'base_amount'),'Base de gastos interiores corrientes; revisar documentación')
        put('29',total(expenses,'deductible_tax_amount'),'Cuotas interiores corrientes explícitamente deducibles')
        put('45',D(boxes['29']),'29; otras deducciones y regularizaciones fuera de ámbito')
        put('46',D(boxes['27'])-D(boxes['45']),'27 - 45')
        put('64',D(boxes['46']),'46; sin régimen simplificado')
        put('65',D('100'),'Tributación exclusiva ante AEAT')
        put('66',D(boxes['64']),'64 × 100%')
        put('110',request.prior_vat_credit,'Saldo pendiente declarado de períodos anteriores')
        applied=min(max(D(boxes['66']),ZERO),request.prior_vat_credit) if request.apply_prior_vat_credit else ZERO
        put('78',applied,'Mínimo entre 110 y resultado positivo 66, si se opta por compensar')
        put('87',request.prior_vat_credit-applied,'110 - 78; no incluye saldo negativo generado en el período')
        put('69',D(boxes['66'])-applied,'66 - 78; sin importaciones diferidas ni regularizaciones')
        put('71',D(boxes['69']),'69; declaración original sin rectificaciones')
        value=D(boxes['71']);generated=max(-value,ZERO)
        result={'amount':str(money(value)),'direction':'a_ingresar' if value>0 else 'saldo_negativo_sin_solicitud_devolucion' if value<0 else 'cero','prior_credit_remaining':boxes['87'],'credit_generated_this_period':str(money(generated))}
    else:
        put('01',total(incoming,'base_amount'),'Ingresos fiscalmente computables acumulados desde 1 de enero')
        put('02',total(expenses,'deductible_irpf_amount'),'Gastos deducibles revisados acumulados; sin cálculo automático de amortizaciones')
        put('03',D(boxes['01'])-D(boxes['02']),'01 - 02; sin reducciones por rendimientos irregulares')
        put('04',max(D(boxes['03']),ZERO)*D('.20'),'20% del rendimiento positivo; sin deducción Ceuta/Melilla/La Palma')
        put('05',request.prior_130_positive_box07_sum,'Suma de casillas 07 positivas de trimestres anteriores; sin deducción vivienda')
        put('06',total(incoming,'withholding_amount'),'Retenciones e ingresos a cuenta acumulados del año')
        put('07',D(boxes['04'])-D(boxes['05'])-D(boxes['06']),'04 - 05 - 06; conserva el signo')
        put('12',max(D(boxes['07']),ZERO),'Máximo entre 07 y cero; sin actividades agrarias')
        previous=request.previous_year_net_activity_income
        reduction=D('100') if previous<=9000 else D('75') if previous<=10000 else D('50') if previous<=11000 else D('25') if previous<=12000 else ZERO
        put('13',reduction,'Minoración art. 110.3.c según rendimiento neto previo; sin modelo 131 simultáneo')
        put('14',D(boxes['12'])-reduction,'12 - 13; conserva el signo')
        put('15',min(max(D(boxes['14']),ZERO),request.prior_130_unused_negative),'Negativos pendientes anteriores, limitados al importe positivo de 14')
        put('16',ZERO,'Deducción por vivienda excluida del ámbito')
        put('17',D(boxes['14'])-D(boxes['15']),'14 - 15 - 16')
        put('18',ZERO,'Declaración original, no complementaria')
        put('19',D(boxes['17']),'17 - 18')
        value=D(boxes['19']);result={'amount':str(money(value)),'direction':'a_ingresar' if value>0 else 'negativo_compensable_en_el_mismo_ejercicio' if value<0 else 'cero'}
    return {'engine_version':RULE_VERSION,'model':request.model,'year':request.year,'period':request.period,'scope':request.regime,'boxes':boxes,'trace':trace,'result':result,'excluded_from_boxes':excluded,'record_ids':[r['id'] for r in selected],'period_start':start.isoformat(),'period_end_exclusive':end.isoformat(),'input_digest':digest({'company':company,'records':selected,'request':request.model_dump(mode='json')}),'source_url':('https://sede.agenciatributaria.gob.es/Sede/todas-gestiones/impuestos-tasas/iva/modelo-303-iva-autoliquidacion_/instrucciones-2026.html' if request.model=='303' and request.period=='1T' else SOURCES[request.model]),'source_checked_on':'2026-11-09','calculation_status':'calculated_requires_review','filing_ready':False,'notice':'Cálculo determinista del supuesto admitido; revisar casillas, integridad y elegibilidad antes de preparar una presentación oficial.'}
