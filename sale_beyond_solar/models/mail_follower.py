from odoo import api, fields, models


class MailFollower(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if self.search([('res_model', '=', vals.get('res_model')), ('res_id', '=', vals.get('res_id')), ('partner_id', '=', vals.get('partner_id'))]):
            return self
        res = super(MailFollower, self).create(vals)
        return res

    def _get_subscription_data(self, doc_data, pids, cids, include_pshare=False):
        return []
