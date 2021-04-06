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

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'opportunity_id' in vals:
            for rec in self.filtered(lambda l: l.state != 'cancel'):
                if rec.opportunity_id.referral_id:
                    rec.referral_id = rec.opportunity_id.referral_id
                    if rec.referral_id.state == 'draft' and rec.state in ['sale', 'lock']:
                        rec.referral_id.sudo().set_sale_created(rec)
                else:
                    rec.referral_id = False
        return res

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for rec in self:
            if rec.referral_id:
                rec.referral_id.sudo().set_sale_created(rec)
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for rec in self:
            if rec.referral_id and rec.referral_id.sale_id == rec:
                rec.referral_id.sudo().mark_cancel()
        return res

    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        for rec in self:
            if rec.referral_id and rec.referral_id.sale_id == rec:
                rec.referral_id.sudo().mark_draft()
            elif rec.referral_id and rec.referral_id.state == 'cancel':
                rec.referral_id.sudo().sale_id = rec
                rec.referral_id.sudo().mark_draft()
        return res
