import calendar
import json
from datetime import date, timedelta
from importlib.resources import files

from .models import Facts
from .territories import TERRITORIES, territorial_profile
from .storage import digest


def catalogue():
    pack = json.loads(files('agntia_gestoria').joinpath('data/legal_sources.json').read_text(encoding='utf-8'))
    pack['digest'] = digest(pack)
    return pack


def add_months(day, months):
    absolute = day.year*12 + day.month-1 + months
    year, month0 = divmod(absolute, 12)
    return date(year, month0+1, min(day.day, calendar.monthrange(year, month0+1)[1]))


def evaluate(company, today=None):
    today = today or date.today()
    pack = catalogue()
    stale = today > date.fromisoformat(pack['next_review_on'])
    facts = Facts.model_validate(company['facts'])
    sl = company['legal_form'] == 'sl'
    profile = territorial_profile(company)
    common = company['tax_territory'] == 'common' and not profile['multiple_territories'] and all(x == 'common' for x in profile['declared_operation_territories'])
    assignments = profile['tax_administrations']
    if any(any(a != 'aeat' for a in values) for values in assignments.values()):
        common = False
    obligations = []
    def add(key, title, category, source_ids, applies=None, missing=(), due=None, scope=True, explanation=''):
        state = 'outside_coverage' if not scope else 'needs_facts' if applies is None else 'applies' if applies else 'not_applicable'
        obligations.append({'rule_id': key, 'title': title, 'category': category, 'applicability': state,
            'missing_facts': list(missing) if state in ('needs_facts','applies') else [],
            'due_date': due.isoformat() if due and state=='applies' else None,
            'deadline_kind': 'nominal_calendar_date' if due and state=='applies' else 'requires_confirmation',
            'explanation': explanation, 'source_ids': source_ids, 'review_required': True})
    close = facts.fiscal_year_end
    add('census','Revisar alta y datos censales','fiscal',['census','lgt'],True,explanation='Confirmar administración competente, actividad y obligaciones censales. No se presenta el modelo 036.')
    add('invoice-records','Revisar documentación y facturación','accounting',['invoicing','commerce','lgt'],True,explanation='Clasificar originales y validar el tratamiento de cada operación. No emitir facturas desde los borradores del MVP.')
    for key,title,months,source in [('annual-formulation','Preparar formulación de cuentas anuales',3,'lsc'),('annual-books','Preparar legalización de libros',4,'commerce'),('annual-meeting','Preparar junta ordinaria de aprobación',6,'lsc')]:
        add(key,title,'corporate',[source],sl,missing=['fiscal_year_end'] if not close else [],due=add_months(close,months) if close else None,
            explanation='Fecha nominal calculada desde el cierre declarado; revisar cómputo, calendario y circunstancias. No se realiza trámite registral.')
    add('annual-deposit','Preparar depósito de cuentas','corporate',['lsc'],sl,
        missing=['accounts_approved_on'] if sl and not facts.accounts_approved_on else [],
        due=add_months(facts.accounts_approved_on,1) if facts.accounts_approved_on else None,
        explanation='Un mes desde la aprobación real; no se presupone que las cuentas se aprobaron al vencer los seis meses.')
    add('corporate-tax','Revisar declaración del Impuesto sobre Sociedades','fiscal',['is','aeat-calendar'],facts.corporate_taxpayer if sl else False,
        missing=['corporate_taxpayer'] if sl and facts.corporate_taxpayer is None else ['fiscal_year_end'] if sl and not close else [],
        due=add_months(close,6)+timedelta(days=25) if close else None,scope=common,
        explanation='Fecha nominal del art. 124 cuando proceda; verificar norma de la campaña, días inhábiles y domiciliación. Sin cálculo de cuota ni envío.')
    vat = facts.vat_return_required if facts.vat_return_required is not None else True if facts.vat_status=='liable' and facts.vat_periodicity!='unknown' else None
    add('vat-return','Revisar autoliquidación de IVA (posible 303)','fiscal',['vat','aeat-calendar'],vat,
        missing=['vat_status','vat_periodicity','vat_return_required'],scope=common,explanation='Confirmar régimen, operaciones, periodicidad y exclusiones. La exención declarada no descarta otras obligaciones especiales; sin vencimiento automático.')
    irpf = False if sl or facts.irpf_payment_model=='none' else None if facts.irpf_payment_model=='unknown' else True
    add('irpf-payments','Revisar pagos fraccionados de IRPF','fiscal',['irpf','aeat-calendar'],irpf,missing=['irpf_payment_model'],scope=common,
        explanation='Modelo declarado en el perfil: '+facts.irpf_payment_model+'. Comprobar régimen y posibles dispensas; no asignar el 130 a todos los autónomos.')
    withholding = True if True in (facts.withholds_payroll,facts.withholds_professionals) else False if facts.withholds_payroll is False and facts.withholds_professionals is False else None
    add('withholding-111','Revisar retenciones de trabajo/profesionales (posible 111)','fiscal',['irpf','aeat-calendar'],withholding,missing=['withholds_payroll','withholds_professionals'],scope=common,explanation='Verificar los rendimientos satisfechos, periodicidad y modelos anuales relacionados.')
    add('withholding-115','Revisar retenciones de arrendamientos (posible 115)','fiscal',['irpf','aeat-calendar'],facts.withholds_rent,missing=['withholds_rent'],scope=common,explanation='Comprobar sujeción y excepciones de la operación, no solo que exista un alquiler.')
    add('payroll-social','Revisar contratación, altas, cotización y prevención','labour',['lgss','employment','prl'],facts.has_employees,missing=['has_employees'],explanation='Requiere convenio y datos de cada trabajador. No calcula nóminas ni tramita altas.')
    add('reta','Revisar encuadramiento en RETA','labour',['lgss'],facts.reta_required if not sl else None,missing=['reta_required'] if not sl else ['situacion_de_socios_y_administradores'],explanation='No se deduce RETA solo del alta fiscal ni se presume exención para administradores de SL.')
    add('privacy-records','Revisar protección de datos y encargados','privacy',['gdpr','privacy','aepd-pymes'],facts.processes_personal_data,missing=['processes_personal_data'],explanation='Valorar bases jurídicas, tratamientos, contratos y medidas según riesgo. No presupone una exención del registro por tener pocos empleados.')
    sif = facts.sif_in_scope
    if sl and facts.corporate_taxpayer is None and sif is True:
        sif = None
    sif_due = date(2027,1,1) if sl and facts.corporate_taxpayer else date(2027,7,1)
    add('sif-adaptation','Revisar adaptación del sistema de facturación SIF','fiscal',['sif','sif-dates'],sif,missing=['sif_in_scope','corporate_taxpayer'] if sl else ['sif_in_scope'],due=sif_due,scope=common,
        explanation='Calendario AEAT consultado el 09/11/2026. Comprobar ámbito, SII y exclusiones; elegir VERI*FACTU no es lo mismo que factura B2B. Este programa no es un SIF de emisión fiscal.')
    b2b = facts.b2b_einvoice_in_scope if facts.previous_year_turnover_over_8m is not None else (False if facts.b2b_einvoice_in_scope is False else None)
    high = facts.previous_year_turnover_over_8m
    add('b2b-invoices','Preparar adaptación a factura electrónica B2B','fiscal',['b2b-rd','b2b-order','b2b-dates'],b2b,missing=['b2b_einvoice_in_scope','previous_year_turnover_over_8m'],due=date(2027,10,6) if high else date(2028,10,6),scope=common,
        explanation='Expedición/remisión/recepción según ámbito y umbral. Los plazos se computan desde 06/10/2026; revisar operación y futuras modificaciones.')
    add('b2b-events','Preparar comunicación de estados y pagos B2B','fiscal',['b2b-rd','b2b-order','b2b-dates'],b2b,missing=['b2b_einvoice_in_scope','previous_year_turnover_over_8m'],due=date(2027,10,6) if high else date(2028,10,6) if sl else date(2029,10,6),scope=common,
        explanation='La comunicación de estados/pagos tiene una transición propia; no se equipara a la fecha de emisión electrónica.')
    if not common:
        add('territory-review','Confirmar fiscalidad territorial y administraciones','fiscal',['lgt','vat','census'],True,missing=['tax_territory'] if company['tax_territory']=='unknown' else [],explanation='Los perfiles territoriales permiten preparar expedientes en toda España. Las reglas fiscales automáticas de territorio común no se extrapolan a perfiles especiales o mixtos; outside_coverage no significa exención.')
    for territory in profile['declared_operation_territories']:
        title, sources = TERRITORIES[territory]
        if territory == 'common':
            continue
        detail = ('Revisar IGIC, localización de operaciones y obligaciones ante la ATC, además de las estatales que correspondan.' if territory == 'canarias' else
                  'Revisar IPSI, ordenanzas locales y localización de operaciones; no aplicar automáticamente IVA peninsular.' if territory in ('ceuta','melilla') else
                  'Determinar administración y normativa por impuesto según Concierto/Convenio, domicilio, volumen, localización y ejercicio. Puede existir tributación conjunta; revisar también requisitos propios de facturación.')
        add('territory-'+territory, 'Revisión territorial: '+title, 'fiscal', sources, None,
            missing=['puntos_de_conexion_por_impuesto','ejercicio','calendario_y_modelos_territoriales'],
            explanation=detail+' Cobertura de preparación documental; sin liquidación ni presentación automática.')
    if profile['multiple_territories'] or any(len(v)>1 for v in assignments.values()):
        add('multi-administration', 'Revisar tributación ante varias administraciones', 'fiscal',
            ['basque-concert','navarra-agreement','canarias-ref','ipsi','lgt'], None,
            missing=['puntos_de_conexion','porcentajes_por_impuesto_y_periodo'],
            explanation='Las administraciones declaradas no acreditan competencia. Determinar sujeción, normativa, exacción e inspección por separado; no se calcula reparto automático.')
    return {'territorial_profile':profile,'company_id':company['id'],'company_revision':company['revision'],'as_of':today.isoformat(),'pack_id':pack['pack_id'],'pack_digest':pack['digest'],
            'pack_checked_on':pack['checked_on'],'pack_stale':stale,'review_required':True,'obligations':obligations,
            'warnings':(['El paquete de fuentes necesita una nueva revisión normativa.'] if stale else [])+['Fechas nominales: confirmar calendario oficial y caso concreto. No hay presentaciones telemáticas en este MVP.']}
