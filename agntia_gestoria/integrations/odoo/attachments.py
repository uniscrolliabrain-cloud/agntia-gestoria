import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
from ...storage import canonical,identifier,now,uid
from ..errors import reject
from .evidence import event
from .vault import store_blob


class Attachments:
    def attachment_metadata(self,actor,cid,invoice_id):
        connection,server=self.scope(actor,cid,'invoices.read');self.require_capability(connection,'attachments.read')
        with self.db.connection() as c:
            if not c.execute('SELECT 1 FROM external_links WHERE connection_id=? AND model=? AND external_id=? AND local_kind=?',(connection['id'],'account.move',str(invoice_id),'invoice')).fetchone():reject('not_found','Factura importada no encontrada',404)
        result=self.client(actor,cid,'invoices.read',connection).call('agntia.bridge','attachment_metadata',{'company_id':server.odoo_company_id,'invoice_id':invoice_id})
        if not isinstance(result,list) or len(result)>100:reject('invalid_response','Metadatos documentales inválidos',502)
        return result

    def download_attachment(self,actor,cid,invoice_id,attachment_id,correlation):
        connection,server=self.scope(actor,cid,'attachments.download');self.require_capability(connection,'attachments.read')
        with self.db.connection() as c:
            invoice=c.execute('SELECT body FROM external_links WHERE connection_id=? AND model=? AND external_id=? AND local_kind=?',(connection['id'],'account.move',str(invoice_id),'invoice')).fetchone()
            if not invoice:reject('not_found','Factura importada no encontrada',404)
            existing=c.execute('SELECT body FROM external_links WHERE connection_id=? AND model=? AND external_id=? AND local_kind=?',(connection['id'],'ir.attachment',str(attachment_id),'document')).fetchone()
        remote=self.client(actor,cid,'attachments.download',connection).call('agntia.bridge','attachment_content',{'company_id':server.odoo_company_id,'invoice_id':invoice_id,'attachment_id':attachment_id})
        try:
            if remote['invoice_id']!=invoice_id or remote['company_id']!=server.odoo_company_id or remote['id']!=attachment_id:raise ValueError()
            raw=base64.b64decode(remote['data'],validate=True)
            if not raw or len(raw)>4*1024*1024:raise ValueError()
            hashed=hashlib.sha256(raw).hexdigest()
            if remote['sha256']!=hashed:raise ValueError()
        except (KeyError,ValueError,TypeError):reject('invalid_attachment','Adjunto remoto inválido',502)
        if existing:
            link=json.loads(existing['body'])
            if link['source_hash']==hashed:
                with self.db.connection() as c:return self.db.get(c,cid,link['local_id'],'document')
            reject('attachment_changed','El original remoto ha cambiado; requiere expediente de rectificación documental',409)
        name=Path(str(remote.get('name') or 'documento').replace('\\','/')).name[:160];suffix=Path(name).suffix.lower()
        signatures={'.pdf':b'%PDF-','.png':b'\x89PNG\r\n\x1a\n','.jpg':b'\xff\xd8\xff','.jpeg':b'\xff\xd8\xff'}
        if suffix in signatures:
            if not raw.startswith(signatures[suffix]):reject('invalid_attachment','El tipo documental no coincide con su contenido',422)
        elif suffix in ('.txt','.csv'):
            try:raw.decode('utf-8-sig')
            except UnicodeError:reject('invalid_attachment','Texto no UTF-8',422)
            if b'\0' in raw:reject('invalid_attachment','Texto binario no permitido',422)
        else:reject('unsupported_attachment','Tipo de adjunto no admitido',422)
        # A temporary plaintext file exists only when an approved scanner requires a path.
        scanner=os.getenv('ODOO_SCANNER_COMMAND_JSON','');scan_status='not_configured'
        if scanner:
            import tempfile
            try:
                argv=json.loads(scanner)
                if not isinstance(argv,list) or not argv or not all(isinstance(x,str) for x in argv):raise ValueError()
                with tempfile.TemporaryDirectory() as folder:
                    path=Path(folder)/('scan'+suffix);path.write_bytes(raw)
                    outcome=subprocess.run([*argv,str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30,check=False)
                    if outcome.returncode!=0:reject('malware_scan_failed','El escáner rechazó el adjunto',422)
                    scan_status='passed'
            except (ValueError,OSError,subprocess.TimeoutExpired):reject('scanner_unavailable','Escáner no disponible; adjunto no guardado',503)
        elif os.getenv('ODOO_REQUIRE_SCANNER','true').lower()=='true':reject('scanner_required','Se requiere un escáner configurado para descargar adjuntos',424)
        did=uid();folder=self.db.root/'documents'/cid;folder.mkdir(parents=True,exist_ok=True);target=folder/(did+'.encrypted')
        store_blob(target,raw)
        document={'id':did,'company_id':cid,'name':name,'stored_name':target.name,'size':len(raw),'sha256':hashed,'created_at':now(),'created_by':actor.id,'content_untrusted':True,'status':'original_unverified','encrypted':True,'scanner_status':scan_status,'source_system':'odoo_community','original_custodian':'odoo','source_invoice_id':invoice_id,'source_attachment_id':attachment_id}
        try:
            with self.db.transaction() as c:
                self.db.put(c,cid,'document',document);self._link(c,connection,'ir.attachment',attachment_id,'document',did,hashed,None,remote_invoice_id=invoice_id)
                self.db.audit(c,cid,actor,'integration.document.stored',did,document);event(self.db,c,connection,actor,'review.required',{'evidenceIds':[did],'operation':'document_received'},correlation)
        except Exception:target.unlink(missing_ok=True);raise
        return document
