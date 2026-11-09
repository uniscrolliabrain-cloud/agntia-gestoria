from fastapi import Depends, Query
from fastapi.responses import Response
from pydantic import Field
from .analytics import analyze, infographic, presentation, report_html, report_pdf
from .auth import Actor,authenticate,company_access,require_role
from .models import Model
from .storage import identifier,uid


def register_report_routes(app,db):
    def access(c,cid,actor):
        identifier(cid);company_access(actor,cid);return db.company(c,cid)
    def build(c,cid,year,company):
        return analyze(company,db.list(c,cid,'tax_record'),db.list(c,cid,'tax_calculation'),db.list(c,cid,'case'),year)
    class ReportRequest(Model):
        year:int=Field(ge=2000,le=2100)

    @app.get('/api/companies/{cid}/dashboard')
    def dashboard(cid:str,year:int=Query(ge=2000,le=2100),actor:Actor=Depends(authenticate)):
        with db.connection() as c:return build(c,cid,year,access(c,cid,actor))

    @app.post('/api/companies/{cid}/reports')
    def create_report(cid:str,body:ReportRequest,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer','agent')
        with db.transaction() as c:
            company=access(c,cid,actor);report=build(c,cid,body.year,company);report.update(id=uid(),created_by=actor.id)
            db.put(c,cid,'report',report);db.audit(c,cid,actor,'report.created',report['id'],report)
        return report

    @app.get('/api/companies/{cid}/reports')
    def reports(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as c:
            company=access(c,cid,actor);current=build(c,cid,2000,company)['report_fingerprint']
            return [{**r,'data_changed_since_report':r.get('report_fingerprint')!=current} for r in db.list(c,cid,'report')]

    @app.get('/api/companies/{cid}/reports/{oid}/download/{format}')
    def download_report(cid:str,oid:str,format:str,actor:Actor=Depends(authenticate)):
        with db.connection() as c:access(c,cid,actor);report=db.get(c,cid,oid,'report')
        generators={'svg':(infographic,'image/svg+xml'),'html':(report_html,'text/html'),'pptx':(presentation,'application/vnd.openxmlformats-officedocument.presentationml.presentation'),'pdf':(report_pdf,'application/pdf')}
        if format not in generators:raise ValueError('Formato permitido: svg, html, pptx o pdf')
        function,media=generators[format]
        return Response(function(report),media_type=media,headers={'Content-Disposition':f'attachment; filename="informe-{report["year"]}.{format}"'})
