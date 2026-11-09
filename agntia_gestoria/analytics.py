"""Explainable analytics from immutable records, without external data disclosure."""
from collections import defaultdict
from datetime import date
from decimal import Decimal
from html import escape
from io import BytesIO
from statistics import median

from .storage import digest, now

D=Decimal

def amount(value):return str(D(value).quantize(D('.01')))

def analyze(company,records,calculations,cases,year):
    selected=[r for r in records if r['status']!='void' and date.fromisoformat(r['operation_date']).year==year]
    income=[r for r in selected if r['kind']=='income'];expense=[r for r in selected if r['kind']=='expense']
    total=lambda rows,key:sum((D(r[key]) for r in rows),D(0))
    revenue=total(income,'base_amount');cost=total(expense,'base_amount');net=revenue-cost
    months=[]
    for month in range(1,13):
        rows=[r for r in selected if date.fromisoformat(r['operation_date']).month==month]
        sales=total([r for r in rows if r['kind']=='income'],'base_amount');spend=total([r for r in rows if r['kind']=='expense'],'base_amount')
        months.append({'month':f'{year}-{month:02}','income':amount(sales),'expenses':amount(spend),'operating_difference':amount(sales-spend),'record_count':len(rows)})
    categories=defaultdict(lambda:D(0));customers=defaultdict(lambda:D(0))
    for r in expense:categories[r.get('category','other')]+=D(r['base_amount'])
    for r in income:customers[r.get('counterparty') or 'Sin identificar']+=D(r['base_amount'])
    fingerprint=digest({'company':company,'records':sorted(records,key=lambda r:r['id'])})
    current={}
    for c in sorted(calculations,key=lambda c:(c['created_at'],c['id'])):
        if c['year']==year:current[(c['model'],c['period'])]=c
    tax=[{'id':c['id'],'model':c['model'],'period':c['period'],'amount':c['result']['amount'],'direction':c['result']['direction'],'stale':c['data_fingerprint']!=fingerprint,'source_url':c['source_url']} for c in current.values()]
    alerts=[]
    def alert(code,title,detail,ids=(),severity='review'):
        alerts.append({'code':code,'title':title,'detail':detail,'record_ids':list(ids),'severity':severity})
    missing=[r['id'] for r in selected if not r.get('document_ids')]
    unreviewed=[r['id'] for r in selected if r['status']!='reviewed']
    if missing:alert('missing_documents','Faltan justificantes',f'{len(missing)} registros no tienen documentos vinculados.',missing)
    if unreviewed:alert('unreviewed','Datos pendientes de revisión',f'{len(unreviewed)} registros no han sido revisados por una persona autorizada.',unreviewed)
    groups=defaultdict(list)
    for r in selected:
        groups[(r['operation_date'],r['kind'],amount(r['base_amount']),amount(r['tax_amount']),(r.get('counterparty') or '').casefold().strip())].append(r['id'])
    for ids in groups.values():
        if len(ids)>1:alert('possible_duplicate','Posible duplicado','Coinciden fecha, clase, importes y contraparte. No se elimina automáticamente.',ids)
    values=[D(r['base_amount']) for r in expense if D(r['base_amount'])>0]
    if len(values)>=5:
        typical=median(values)
        outliers=[r['id'] for r in expense if D(r['base_amount'])>typical*3]
        if outliers:alert('expense_outlier','Gastos superiores al patrón habitual','Superan tres veces la mediana de los gastos positivos; puede haber una explicación normal.',outliers)
    previous=[m for m in months if m['record_count']]
    if len(previous)>=2:
        before,latest=previous[-2:]
        if D(before['income'])>0 and D(latest['income'])<D(before['income'])*D('.8'):
            alert('income_change','Menos ingresos en el último mes con datos',f"{latest['month']} frente a {before['month']}; comprobar períodos incompletos. No es una previsión.")
    identifiable={k:v for k,v in customers.items() if k!='Sin identificar' and v>0}
    if revenue>0 and identifiable and max(identifiable.values())/revenue>D('.5'):
        alert('concentration','Concentración de ingresos','Una contraparte identificada representa más del 50% de los ingresos registrados.')
    if any(t['stale'] for t in tax):alert('stale_calculation','Cálculos pendientes de actualización','Los datos han cambiado desde el cálculo; sus importes no se consideran actuales.')
    other=[r['id'] for r in selected if r['kind'] not in ('income','expense')]
    if other:alert('unallocated_records','Ajustes o retenciones separados',f'{len(other)} registros no se incluyen automáticamente en ingresos y gastos; revisar su imputación.',other)
    if not selected:alert('empty','Sin datos para el ejercicio','Importa registros reales; no se generan cifras de ejemplo automáticamente.',severity='info')
    if net<0:alert('negative_operating_difference','Gastos registrados superiores a ingresos','La diferencia de bases es negativa; no equivale por sí sola a una pérdida contable o fiscal.')
    return {'company_id':company['id'],'company_name':company['name'],'year':year,'generated_at':now(),'data_fingerprint':fingerprint,
        'report_fingerprint':digest({'company':company,'records':sorted(records,key=lambda r:r['id']),'calculations':sorted(calculations,key=lambda r:r['id']),'cases':sorted(cases,key=lambda r:r['id'])}),'metrics':{'income_base':amount(revenue),'expense_base':amount(cost),'operating_difference':amount(net),'operating_margin_percent':str((net/revenue*100).quantize(D('.01'))) if revenue>0 else None,'record_count':len(selected),'reviewed_count':len(selected)-len(unreviewed),'missing_document_count':len(missing),'withholding_on_income':amount(total(income,'withholding_amount'))},
        'months':months,'expense_categories':[{'category':k,'amount':amount(v)} for k,v in sorted(categories.items(),key=lambda x:-x[1])],
        'customer_income':[{'counterparty':k,'amount':amount(v)} for k,v in sorted(customers.items(),key=lambda x:-x[1])],
        'tax_calculations':tax,'alerts':alerts,'open_cases':len([c for c in cases if c['status']!='done']),
        'record_ids':[r['id'] for r in selected],'definitions':{'operating_difference':'Ingresos menos gastos registrados, sin impuestos indirectos. No es beneficio contable, base fiscal ni flujo de caja.','data_status':'Incluye registros pendientes de revisión, identificados en las métricas.','intelligence':'Reglas explicables: duplicados, justificantes, concentración, cambios y atípicos; ningún dato se envía a un proveedor de IA.'}}


def infographic(report):
    """Standalone SVG with escaped labels and a zero baseline including negative values."""
    months=report['months'];values=[D(m[k]) for m in months for k in ('income','expenses')]
    lo=min([D(0)]+values);hi=max([D(1)]+values);span=hi-lo
    y=lambda v:float(D('350')-(v-lo)/span*D('210'))
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="590" viewBox="0 0 1100 590" role="img" aria-labelledby="title desc">',f'<title id="title">{escape(report["company_name"])} · {report["year"]}</title>','<desc id="desc">Ingresos y gastos mensuales de los registros de la empresa; importes en EUR, incluye datos pendientes de revisión.</desc>','<rect width="1100" height="590" rx="24" fill="#f4f8f6"/>',f'<text x="40" y="48" font-family="sans-serif" font-size="25" fill="#183e34">{escape(report["company_name"][:60])} · {report["year"]}</text>']
    for i,(label,key) in enumerate([('Ingresos registrados','income_base'),('Gastos registrados','expense_base'),('Diferencia operativa','operating_difference')]):
        x=40+i*355;parts.extend([f'<text x="{x}" y="88" font-family="sans-serif" font-size="14" fill="#576e64">{label}</text>',f'<text x="{x}" y="121" font-family="sans-serif" font-size="27" fill="#183e34">{report["metrics"][key]} EUR</text>'])
    parts.append(f'<line x1="40" y1="{y(D(0))}" x2="1060" y2="{y(D(0))}" stroke="#8ba69a"/>')
    for i,m in enumerate(months):
        x=48+i*84
        for offset,key,color in [(0,'income','#28735a'),(25,'expenses','#d99a53')]:
            v=D(m[key]);top=min(y(v),y(D(0)));height=abs(y(v)-y(D(0)))
            parts.append(f'<rect x="{x+offset}" y="{top:.2f}" width="21" height="{height:.2f}" rx="3" fill="{color}"><title>{m["month"]} {key}: {amount(v)} EUR</title></rect>')
        parts.append(f'<text x="{x}" y="380" font-family="sans-serif" font-size="13" fill="#576e64">{m["month"][-2:]}</text>')
    parts.extend(['<text x="40" y="415" font-family="sans-serif" font-size="14" fill="#28735a">Ingresos (verde) · Gastos (ocre) · EUR</text>',f'<text x="40" y="454" font-family="sans-serif" font-size="15" fill="#183e34">{report["metrics"]["record_count"]} registros · {report["metrics"]["reviewed_count"]} revisados · {report["metrics"]["missing_document_count"]} sin justificante</text>','<text x="40" y="491" font-family="sans-serif" font-size="13" fill="#576e64">Diferencia de bases registradas: no equivale a beneficio contable, renta fiscal o caja.</text>',f'<text x="40" y="520" font-family="sans-serif" font-size="12" fill="#576e64">Fuente: registros de la empresa · {escape(report["generated_at"])}.</text>','</svg>'])
    return ''.join(parts)


def report_html(report):
    title=escape(report['company_name']);items=''.join('<li><b>'+escape(a['title'])+'</b>: '+escape(a['detail'])+'</li>' for a in report['alerts'])
    return '<!doctype html><html lang="es"><meta charset="utf-8"><title>Informe '+title+'</title><style>body{font:16px system-ui;max-width:1100px;margin:30px auto;padding:20px;color:#183e34}svg{width:100%;height:auto}li{margin:18px 0}p{line-height:1.6}@media print{body{margin:0}svg{max-height:70vh}}</style><h1>Informe de gestión · '+title+'</h1>'+infographic(report)+'<h2>Hallazgos y próximos pasos</h2><ul>'+items+'</ul><h2>Cómo interpretar los datos</h2>'+''.join('<p>'+escape(v)+'</p>' for v in report['definitions'].values())+'<p>Huella de datos: '+report['data_fingerprint']+'</p></html>'


def presentation(report):
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    deck=Presentation();deck.slide_width=Inches(13.33);deck.slide_height=Inches(7.5)
    def slide(title,lines):
        s=deck.slides.add_slide(deck.slide_layouts[1]);s.shapes.title.text=title
        tf=s.placeholders[1].text_frame;tf.clear()
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.size=Pt(21)
        return s
    m=report['metrics']
    slide(report['company_name']+' · '+str(report['year']),['Informe de gestión basado en registros de la empresa',f"Ingresos: {m['income_base']} EUR · Gastos: {m['expense_base']} EUR",f"Diferencia operativa: {m['operating_difference']} EUR",f"{m['record_count']} registros · {m['reviewed_count']} revisados",'La diferencia operativa no es beneficio contable ni caja.'])
    s=deck.slides.add_slide(deck.slide_layouts[5]);s.shapes.title.text='Evolución mensual · EUR'
    chart=CategoryChartData();chart.categories=[x['month'][-2:] for x in report['months']]
    for name,key in [('Ingresos','income'),('Gastos','expenses')]:chart.add_series(name,[float(x[key]) for x in report['months']])
    s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(.8),Inches(1.5),Inches(11.7),Inches(5),chart)
    slide('Composición de gastos',[f"{x['category']}: {x['amount']} EUR" for x in report['expense_categories'][:10]] or ['Sin gastos registrados'])
    alerts=report['alerts']
    for offset in range(0,max(len(alerts),1),5):slide('Hallazgos y acciones',[a['title']+': '+a['detail'] for a in alerts[offset:offset+5]] or ['Sin alertas con las reglas actuales; no acredita que los datos estén completos.'])
    slide('Cálculos fiscales disponibles',[f"Modelo {t['model']} · {t['period']}: {t['amount']} EUR · "+('DATOS MODIFICADOS' if t['stale'] else 'requiere revisión') for t in report['tax_calculations'][:8]] or ['Sin cálculos guardados para el ejercicio'])
    slide('Fuentes y límites',['Datos: registros internos de la empresa, incluidos los pendientes de revisión.','Análisis mediante reglas explicables; no hay predicciones ni datos inventados.','Exportado: '+report['generated_at'],'Huella: '+report['data_fingerprint']])
    output=BytesIO();deck.save(output);return output.getvalue()


def report_pdf(report):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
    output=BytesIO();styles=getSampleStyleSheet();doc=SimpleDocTemplate(output)
    story=[Paragraph(escape(report['company_name'])+' · '+str(report['year']),styles['Title'])]
    for label,key in [('Ingresos','income_base'),('Gastos','expense_base'),('Diferencia operativa','operating_difference')]:story.append(Paragraph(label+': '+report['metrics'][key]+' EUR',styles['Heading2']))
    story.append(Paragraph(escape(report['definitions']['operating_difference']),styles['BodyText']))
    rows=[['Mes','Ingresos EUR','Gastos EUR','Diferencia EUR']]+[[m['month'],m['income'],m['expenses'],m['operating_difference']] for m in report['months']]
    table=Table(rows,repeatRows=1);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d5e7db')),('GRID',(0,0),(-1,-1),.25,colors.lightgrey)]));story.extend([Spacer(1,18),table,Spacer(1,18)])
    for t in report['tax_calculations']:
        story.append(Paragraph(f"Modelo {t['model']} {t['period']}: {t['amount']} EUR · "+('datos modificados' if t['stale'] else 'requiere revisión'),styles['BodyText']))
    for a in report['alerts']:story.extend([Paragraph(escape(a['title']),styles['Heading3']),Paragraph(escape(a['detail']),styles['BodyText'])])
    for value in report['definitions'].values():story.append(Paragraph(escape(value),styles['BodyText']))
    story.append(Paragraph('Datos: '+report['generated_at']+' · '+report['data_fingerprint'],styles['BodyText']));doc.build(story);return output.getvalue()
