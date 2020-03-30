from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    referral_id = fields.Many2one(comodel_name='sale.referral', string="Referral")

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.opportunity_id.referral_id:
            res.referral_id = res.opportunity_id.referral_id
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            if rec.referral_id:
                rec.referral_id.set_sale_created(rec)
        return res
