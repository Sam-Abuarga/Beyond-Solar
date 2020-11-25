from odoo import api, fields, models
from odoo.addons.sale_management.models.sale_order import SaleOrder as SaleOrderEmail


def action_confirm(self):
    res = super(SaleOrderEmail, self).action_confirm()
    for order in self:
        if order.sale_order_template_id and order.sale_order_template_id.mail_template_id:
            self.sale_order_template_id.mail_template_id.send_mail(order.id, email_values={'subtype_id': 1})
    return res

SaleOrderEmail.action_confirm = action_confirm


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_battery = fields.Boolean(string="Has Battery", compute='_compute_line_categories', store=True)
    has_micro_inverter = fields.Boolean(string="Has Micro Inverter", compute='_compute_line_categories', store=True)
    has_inverter = fields.Boolean(string="Has Inverter", compute='_compute_line_categories', store=True)
    has_panel = fields.Boolean(string="Has Panel", compute='_compute_line_categories', store=True)

    filtered_sale_order_option_ids = fields.One2many(comodel_name='sale.order.option', inverse_name='order_id', domain=[('is_present', '=', True)],
                                                     string='Optional Products Lines', copy=True, readonly=False)

    @api.depends('order_line.product_id')
    def _compute_line_categories(self):
        battery_cat = self.env['product.category'].search([('name', '=', "Storage")], limit=1)
        micro_cat = self.env['product.category'].search([('name', '=', "Micro Inverters")], limit=1)
        inverter_cat = self.env['product.category'].search([('name', '=', "Inverters")], limit=1)
        panel_cat = self.env['product.category'].search([('name', '=', "Solar Panels")], limit=1)

        battery_cat_ids = self.env['product.category'].search([('id', 'child_of', battery_cat.id)]).ids
        micro_cat_ids = self.env['product.category'].search([('id', 'child_of', micro_cat.id)]).ids
        inverter_cat_ids = self.env['product.category'].search([('id', 'child_of', inverter_cat.id)]).ids
        panel_cat_ids = self.env['product.category'].search([('id', 'child_of', panel_cat.id)]).ids

        for rec in self:
            battery = False
            micro = False
            inverter = False
            panel = False

            for line in rec.order_line:
                id = line.product_id.categ_id.id
                if id in battery_cat_ids:
                    battery = True
                if id in micro_cat_ids:
                    micro = True
                if id in inverter_cat_ids:
                    inverter = True
                if id in panel_cat_ids:
                    panel = True

            rec.has_battery = battery
            rec.has_micro_inverter = micro
            rec.has_inverter = inverter
            rec.has_panel = panel
