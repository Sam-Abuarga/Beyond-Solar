from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    referral_partner_id = fields.Many2one(comodel_name='res.partner', string="Referred By")
    referral_id = fields.Many2one(comodel_name='sale.referral', string="Referral")
    referred = fields.Char(string="Referral Notes")  # Change inbuilt char field label

    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        if res.referral_partner_id:
            res.create_referral()
        return res

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        for rec in self:
            if rec.referral_partner_id and not rec.referral_id:
                rec.create_referral()
        return res

    def create_referral(self):
        for rec in self:
            if not rec.referral_id:
                rec.referral_id = self.env['sale.referral'].create({
                    'state': 'draft',
                    'lead_id': rec.id,
                    'partner_id': rec.referral_partner_id.id
                })
