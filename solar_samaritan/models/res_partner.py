from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    referral_ids = fields.One2many(comodel_name='sale.referral', inverse_name='partner_id', string="Referrals")
    indirect_referral_ids = fields.Many2many(comodel_name='sale.referral', compute='_compute_indirect_referrals', string="Indirect Referrals")
    referred_by_id = fields.Many2one(comodel_name='sale.referral', compute='_compute_referred_by')

    def _compute_indirect_referrals(self):
        for rec in self:
            referrals = rec.referral_ids
            referred_partners = rec.referral_ids.mapped('sale_id.partner_id') | rec.referral_ids.mapped('lead_id.partner_id')
            current = referred_partners

            while current:
                current = (referred_partners.mapped('referral_ids.sale_id.partner_id') | referred_partners.mapped('referral_ids.lead_id.partner_id')) - referred_partners
                referrals |= current.referral_ids
                if current:
                    referred_partners |= current

            rec.indirect_referral_ids = referrals - rec.referral_ids

    def _compute_referred_by(self):
        for rec in self:
            rec.referred_by_id = self.env['sale.referral'].search(['|', ('lead_id.partner_id', '=', rec.id), ('sale_id.partner_id', '=', rec.id)], limit=1)

    def get_referral_view(self):
        return {
            'name': 'Referrals',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.referral',
            'domain': [('id', 'in', (self.referral_ids | self.indirect_referral_ids).ids)],
            'view_mode': 'form',
            'view_type': 'kanban,tree,form',
            'views': [
                (self.env.ref('solar_samaritan.sale_referral_kanban_view').id, 'kanban'),
                (self.env.ref('solar_samaritan.sale_referral_tree_view').id, 'tree'),
                (self.env.ref('solar_samaritan.sale_referral_form_view').id, 'form')
            ],
            'target': 'current',
            'context': dict(self._context),
        }
