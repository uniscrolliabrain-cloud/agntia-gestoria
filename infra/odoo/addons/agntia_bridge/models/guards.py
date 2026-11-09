"""A leaked API key alone must not bypass the business bridge via generic create/write.
The in-process marker is an object identity that cannot be forged in JSON context.
"""
from odoo import api,models
from odoo.exceptions import AccessError
from .bridge import _WRITE_TOKEN


def guarded(record):return record.env.user.has_group('agntia_bridge.group_integration')
def require_internal(record):
    if guarded(record) and record.env.context.get('_agntia_internal_write') is not _WRITE_TOKEN:raise AccessError('Use the signed Agntia business bridge')


class Partner(models.Model):
    _inherit='res.partner'
    @api.model_create_multi
    def create(self,vals_list):
        require_internal(self)
        if guarded(self) and any(v.get('company_id')!=self.env.company.id for v in vals_list):raise AccessError('Company required')
        return super().create(vals_list)
    def write(self,vals):
        require_internal(self)
        if guarded(self) and (any(r.company_id!=self.env.company for r in self) or 'company_id' in vals):raise AccessError('Company mutation denied')
        return super().write(vals)
    def unlink(self):
        if guarded(self):raise AccessError('Deletion denied')
        return super().unlink()
