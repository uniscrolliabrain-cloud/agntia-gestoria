from odoo import api,models
from odoo.exceptions import AccessError
from odoo.addons.agntia_bridge.models.guards import require_internal,guarded


class Move(models.Model):
    _inherit='account.move'
    @api.model_create_multi
    def create(self,vals_list):
        require_internal(self)
        if guarded(self) and any(v.get('state','draft')!='draft' or v.get('move_type')!='out_invoice' or v.get('company_id')!=self.env.company.id for v in vals_list):raise AccessError('Only own-company customer drafts permitted')
        return super().create(vals_list)
    def write(self,vals):
        require_internal(self)
        if guarded(self) and (any(m.state!='draft' or m.company_id!=self.env.company for m in self) or vals.get('state','draft')!='draft' or 'company_id' in vals):raise AccessError('Only draft changes permitted')
        return super().write(vals)
    def _post(self,*args,**kwargs):
        if guarded(self):raise AccessError('Posting forbidden for integration principal')
        return super()._post(*args,**kwargs)
    def unlink(self):
        if guarded(self):raise AccessError('Deletion forbidden for integration principal')
        return super().unlink()


class Line(models.Model):
    _inherit='account.move.line'
    @api.model_create_multi
    def create(self,vals_list):
        require_internal(self)
        if guarded(self):
            moves=self.env['account.move'].browse([v['move_id'] for v in vals_list if v.get('move_id')])
            if any(m.state!='draft' or m.company_id!=self.env.company for m in moves):raise AccessError('Draft lines only')
        return super().create(vals_list)
    def write(self,vals):
        require_internal(self)
        if guarded(self) and (any(l.move_id.state!='draft' or l.company_id!=self.env.company for l in self) or 'move_id' in vals or 'company_id' in vals):raise AccessError('Only draft lines permitted')
        return super().write(vals)
    def unlink(self):
        require_internal(self)
        if guarded(self) and any(l.move_id.state!='draft' for l in self):raise AccessError('Only transient draft recomputation permitted')
        return super().unlink()
