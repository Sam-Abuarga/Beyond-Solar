from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    referral_ids = fields.One2many(comodel_name='sale.referral', inverse_name='partner_id', string="Referrals")
    indirect_referral_ids = fields.Many2many(comodel_name='res.partner', compute='_compute_indirect_referrals')
    referred_by_id = fields.Many2one(comodel_name='sale.referral', compute='_compute_referred_by')

    def _compute_indirect_referrals(self):
        for rec in self:
            referred_partners = rec.referral_ids.mapped('sale_id.partner_id') | rec.referral_ids.mapped('lead_id.partner_id')
            current = referred_partners
            while current:
                current = (referred_partners.mapped('referral_ids.sale_id.partner_id') | referred_partners.mapped('referral_ids.lead_id.partner_id')) - referred_partners
                if current:
                    referred_partners |= current
            rec.indirect_referral_ids = referred_partners - rec.referral_ids.mapped('sale_id.partner_id') - rec.referral_ids.mapped('lead_id.partner_id')

    def _compute_referred_by(self):
        for rec in self:
            rec.referred_by_id = self.env['sale.referral'].search(['|', ('lead_id.partner_id', '=', rec.id), ('sale_id.partner_id', '=', rec.id)], limit=1)
