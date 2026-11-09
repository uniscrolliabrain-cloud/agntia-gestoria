"""Persist economic facts and preparation snapshots; never infer filing eligibility."""
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import Depends, HTTPException, UploadFile, File
from pydantic import Field, model_validator

from .auth import Actor, authenticate, company_access, require_role
from .models import Model, Revision
from .rules import catalogue
from .engines import Calculation, calculate
from .storage import digest, identifier, now, uid


class TaxRecord(Model):
    external_id: str = Field(min_length=1,max_length=160)
    operation_date: date
    kind: Literal['income','expense','withholding','adjustment']
    description: str = Field(min_length=2,max_length=1000)
    tax_kind: Literal['iva','igic','ipsi','none','other']
    base_amount: Decimal = Field(ge=-1000000000000,le=1000000000000,decimal_places=2)
    tax_amount: Decimal = Field(ge=-1000000000000,le=1000000000000,decimal_places=2)
    withholding_amount: Decimal = Field(default=Decimal('0'),ge=-1000000000000,le=1000000000000,decimal_places=2)
    document_ids: list[str] = Field(default_factory=list,max_length=100)
    category: Literal['ordinary','asset','payroll','rent','agricultural','other'] = 'other'
    counterparty: str = Field(default='',max_length=200)
    vat_treatment: Literal['domestic_current','investment','intra_eu','import','cash','exempt','other'] = 'other'
    tax_rate: Decimal|None = Field(default=None,ge=0,le=100,decimal_places=4)
    deductible_tax_amount: Decimal|None = Field(default=None,ge=0,le=1000000000000,decimal_places=2)
    deductible_irpf_amount: Decimal|None = Field(default=None,ge=0,le=1000000000000,decimal_places=2)
    classification_notes: str = Field(default='',max_length=5000)

    @model_validator(mode='after')
    def tax_consistency(self):
        if self.tax_kind == 'none' and self.tax_amount:
            raise ValueError('Un registro sin impuesto no puede tener cuota')
        if self.deductible_tax_amount is not None and self.deductible_tax_amount>max(self.tax_amount,0):raise ValueError('La cuota deducible no puede superar la soportada positiva')
        if self.deductible_irpf_amount is not None and self.deductible_irpf_amount>max(self.base_amount+self.tax_amount,0):raise ValueError('El gasto deducible supera el importe registrado')
        return self


class Preparation(Model):
    model: Literal['100','130','131','303','390','111','190','115','180','200','202','347','349','territorial']
    year: int = Field(ge=2000,le=2100)
    period: Literal['annual','1T','2T','3T','4T','01','02','03','04','05','06','07','08','09','10','11','12']
    administration: Literal['aeat','atc','araba','bizkaia','gipuzkoa','navarra','ceuta','melilla']

    @model_validator(mode='after')
    def period_validity(self):
        annual={'100','390','190','180','200','347'}
        if self.model in annual and self.period != 'annual':
            raise ValueError('Este expediente requiere período anual')
        if self.model in ('130','131') and self.period not in ('1T','2T','3T','4T'):
            raise ValueError('Los pagos fraccionados requieren trimestre')
        if self.model in ('303','111','115') and self.period == 'annual':
            raise ValueError('Este modelo no tiene período anual')
        return self


def bounds(year,period):
    if period=='annual': return date(year,1,1),date(year+1,1,1)
    month=(int(period[0])-1)*3+1 if period.endswith('T') else int(period)
    count=3 if period.endswith('T') else 1
    end=month+count
    return date(year,month,1),date(year+1,1,1) if end>12 else date(year,end,1)


def register_tax_routes(app,db):
    def access(c,cid,actor):
        identifier(cid);company_access(actor,cid)
        return db.company(c,cid)

    def fingerprint(c,cid):
        return digest({'company':db.company(c,cid),'records':sorted(db.list(c,cid,'tax_record'),key=lambda r:r['id'])})

    @app.get('/api/tax-capabilities')
    def capabilities(actor:Actor=Depends(authenticate)):
        return {'scope':'Gestoría de pymes y autónomos de toda España',
            'economic_records':True,'preparation_snapshots':True,'data_change_detection':True,
            'official_tax_calculation':False,'bounded_calculation_engines':['303_2026_1T_to_4T_general_domestic','130_2026_1T_to_4T_direct_normal'],'official_filing':False,
            'models':[{'model':m,'status':'bounded_calculation_2026_common' if m in ('303','130') else 'preparation_only'} for m in Preparation.model_fields['model'].annotation.__args__],
            'notice':'La disponibilidad de preparación documental no acredita elegibilidad, cálculo de casillas ni presentación oficial.'}

    class RecordReview(Revision):
        notes:str=Field(min_length=5,max_length=5000)

    @app.post('/api/companies/{cid}/tax-records/{oid}/review')
    def review_record(cid:str,oid:str,body:RecordReview,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer')
        with db.transaction() as c:
            access(c,cid,actor);r=db.get(c,cid,oid,'tax_record')
            if r['revision']!=body.revision or r['status']!='unverified':raise HTTPException(409,'Revisión o estado incorrectos')
            if not r.get('document_ids'):raise ValueError('Vincula documentos antes de revisar el registro')
            r.update(status='reviewed',revision=r['revision']+1,review={'actor_id':actor.id,'notes':body.notes,'at':now()})
            db.put(c,cid,'tax_record',r);db.audit(c,cid,actor,'tax_record.reviewed',oid,r)
        return r

    @app.post('/api/companies/{cid}/tax-calculations')
    def calculate_return(cid:str,body:Calculation,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer','agent')
        with db.transaction() as c:
            company=access(c,cid,actor)
            result=calculate(company,db.list(c,cid,'tax_record'),body)
            result.update(id=uid(),company_id=cid,created_at=now(),created_by=actor.id,inputs=body.model_dump(mode='json'),data_fingerprint=fingerprint(c,cid))
            db.put(c,cid,'tax_calculation',result);db.audit(c,cid,actor,'tax_calculation.created',result['id'],result)
        return result

    @app.get('/api/companies/{cid}/tax-calculations')
    def calculations(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as c:
            access(c,cid,actor);current=fingerprint(c,cid)
            return [{**r,'data_changed_since_calculation':r['data_fingerprint']!=current} for r in db.list(c,cid,'tax_calculation')]

    @app.get('/api/companies/{cid}/tax-records')
    def records(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as c:access(c,cid,actor);return db.list(c,cid,'tax_record')

    @app.post('/api/companies/{cid}/tax-records')
    def create_record(cid:str,body:TaxRecord,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer','agent')
        with db.transaction() as c:
            access(c,cid,actor)
            for did in body.document_ids:db.get(c,cid,did,'document')
            key='tax-record:'+body.external_id
            if c.execute('SELECT 1 FROM objects WHERE company_id=? AND unique_key=?',(cid,key)).fetchone():
                raise HTTPException(409,'Identificador externo ya importado; revisar el registro existente')
            record={**body.model_dump(mode='json'),'id':uid(),'company_id':cid,'revision':0,'status':'unverified','created_at':now(),'created_by':actor.id}
            db.put(c,cid,'tax_record',record,key);db.audit(c,cid,actor,'tax_record.created',record['id'],record)
        return record

    class ImportBatch(Model):
        records:list[TaxRecord]=Field(min_length=1,max_length=2000)

    @app.post('/api/companies/{cid}/tax-records/import')
    def import_records(cid:str,body:ImportBatch,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer','agent')
        ids=[]
        with db.transaction() as c:
            access(c,cid,actor)
            for item in body.records:
                for did in item.document_ids:db.get(c,cid,did,'document')
                key='tax-record:'+item.external_id
                if c.execute('SELECT 1 FROM objects WHERE company_id=? AND unique_key=?',(cid,key)).fetchone():raise HTTPException(409,'Referencia duplicada: '+item.external_id+'; no se importa ningún registro del lote')
                record={**item.model_dump(mode='json'),'id':uid(),'company_id':cid,'revision':0,'status':'unverified','created_at':now(),'created_by':actor.id}
                db.put(c,cid,'tax_record',record,key);db.audit(c,cid,actor,'tax_record.imported',record['id'],record);ids.append(record['id'])
        return {'imported':len(ids),'record_ids':ids}

    @app.post('/api/companies/{cid}/tax-records/preview-csv')
    def preview_csv(cid:str,file:UploadFile=File(...),actor:Actor=Depends(authenticate)):
        import csv,io
        require_role(actor,'owner','reviewer','agent')
        with db.connection() as c:access(c,cid,actor)
        try:raw=file.file.read(5*1024*1024+1)
        finally:file.file.close()
        if len(raw)>5*1024*1024:raise ValueError('CSV máximo: 5 MB')
        text=raw.decode('utf-8-sig');rows=csv.DictReader(io.StringIO(text))
        output=[];errors=[]
        for index,row in enumerate(rows,start=2):
            if index>2001:raise ValueError('CSV máximo: 2000 filas')
            try:
                normalized={k:v for k,v in row.items() if v is not None and v!=''}
                if 'document_ids' in normalized:normalized['document_ids']=[x.strip() for x in normalized['document_ids'].split('|') if x.strip()]
                item=TaxRecord.model_validate(normalized)
                output.append(item.model_dump(mode='json'))
            except (ValueError,TypeError) as exc:errors.append({'line':index,'error':str(exc)[:1500]})
        if not rows.fieldnames:raise ValueError('CSV sin cabecera')
        return {'records':output,'errors':errors,'can_import':bool(output) and not errors,'notice':'Vista previa; no se guarda nada. Clasificación e importes deben revisarse. Fechas ISO, punto decimal y separador coma.'}

    @app.post('/api/companies/{cid}/tax-records/{oid}/void')
    def void_record(cid:str,oid:str,body:Revision,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer','agent')
        with db.transaction() as c:
            access(c,cid,actor);r=db.get(c,cid,oid,'tax_record')
            if r['revision']!=body.revision or r['status']=='void':raise HTTPException(409,'Revisión o estado incorrectos')
            r.update(status='void',revision=r['revision']+1,voided_at=now())
            db.put(c,cid,'tax_record',r);db.audit(c,cid,actor,'tax_record.voided',oid,r)
        return r

    @app.post('/api/companies/{cid}/tax-preparations')
    def prepare(cid:str,body:Preparation,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner','reviewer','agent')
        start,end=bounds(body.year,body.period)
        with db.transaction() as c:
            company=access(c,cid,actor)
            if body.model=='100' and company['legal_form']!='autonomo':
                raise ValueError('La renta es de una persona física, no de una SL; usa el perfil del titular')
            all_records=db.list(c,cid,'tax_record')
            selected=[r for r in all_records if r['status']!='void' and start<=date.fromisoformat(r['operation_date'])<end]
            groups={}
            for r in selected:
                key=r['kind']+':'+r['tax_kind']
                group=groups.setdefault(key,{'count':0,'base_amount':Decimal('0'),'tax_amount':Decimal('0'),'withholding_amount':Decimal('0')})
                group['count']+=1
                for k in ('base_amount','tax_amount','withholding_amount'):group[k]+=Decimal(r[k])
            groups={k:{n:str(v.quantize(Decimal('.01'))) if isinstance(v,Decimal) else v for n,v in g.items()} for k,g in groups.items()}
            blockers=['Motor legal y casillas oficiales no implementados para este modelo/ejercicio/administración.','Registros pendientes de clasificación y comprobación documental.','Representación, conector y validación oficial de presentación no implementados.']
            if not selected:blockers.append('No hay registros en el período; esto no acredita una declaración sin actividad.')
            if body.model=='200':blockers.append('Falta confirmar el período impositivo real de la sociedad; el resumen calendario seleccionado no sustituye un cierre fiscal no coincidente o inferior al año natural.')
            if body.model=='100':blockers.append('Faltan datos personales, familiares y rentas ajenas a la actividad; los libros de empresa no bastan para calcular la renta.')
            if body.model in ('130','131'):blockers.append('Falta el motor del régimen aplicable y sus acumulados, reducciones y excepciones; no aplicar un porcentaje genérico.')
            pack=catalogue()
            preparation={'source_pack_id':pack['pack_id'],'source_pack_digest':pack['digest'],'company_revision':company['revision'],**body.model_dump(mode='json'),'id':uid(),'company_id':cid,'status':'preparation_only','created_at':now(),'created_by':actor.id,'selection_basis':'operation_date_calendar_period_not_a_legal_tax_allocation','period_start':start.isoformat(),'period_end_exclusive':end.isoformat(),'record_ids':[r['id'] for r in selected],'data_fingerprint':fingerprint(c,cid),'arithmetic_summary':groups,'blockers':blockers,'filing_ready':False,'official_tax_result':None,'notice':'Resumen aritmético de datos introducidos; no son casillas ni una declaración calculada o presentada.'}
            db.put(c,cid,'tax_preparation',preparation);db.audit(c,cid,actor,'tax_preparation.created',preparation['id'],preparation)
        return preparation

    @app.get('/api/companies/{cid}/tax-preparations')
    def preparations(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as c:
            access(c,cid,actor);current=fingerprint(c,cid)
            return [{**p,'data_changed_since_preparation':p['data_fingerprint']!=current,'source_pack_changed':p.get('source_pack_digest')!=catalogue()['digest']} for p in db.list(c,cid,'tax_preparation')]
