from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_battery = fields.Boolean(string="Has Battery", compute='_compute_line_categories')
    has_inverter = fields.Boolean(string="Has Inverter", compute='_compute_line_categories')
    has_panel = fields.Boolean(string="Has Panel", compute='_compute_line_categories')

    @api.depends('order_line.product_id')
    def _compute_line_categories(self):
        battery_cat = self.env['product.category'].search([('name', '=', "Storage")], limit=1)
        inverter_cat = self.env['product.category'].search([('name', '=', "Inverters")], limit=1)
        panel_cat = self.env['product.category'].search([('name', '=', "Solar Panels")], limit=1)

        battery_cat_ids = self.env['product.category'].search([('id', 'child_of', battery_cat.id)]).ids
        inverter_cat_ids = self.env['product.category'].search([('id', 'child_of', inverter_cat.id)]).ids
        panel_cat_ids = self.env['product.category'].search([('id', 'child_of', panel_cat.id)]).ids

        for rec in self:
            battery = False
            inverter = False
            panel = False

            for line in rec.order_line:
                id = line.product_id.categ_id.id
                if id in battery_cat_ids:
                    battery = True
                if id in inverter_cat_ids:
                    inverter = True
                if id in panel_cat_ids:
                    panel = True

            rec.has_battery = battery
            rec.has_inverter = inverter
            rec.has_panel = panel
