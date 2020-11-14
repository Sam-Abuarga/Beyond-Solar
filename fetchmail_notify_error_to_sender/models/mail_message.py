from odoo import api, fields, models
from odoo.exceptions import UserError


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _get_default_from(self):
        try:
            return super(MailMessage, self)._get_default_from()
        except UserError:
            return "s.arga@beyondsolar.com.au"
