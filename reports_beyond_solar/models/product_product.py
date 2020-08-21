from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def is_equipment(self):
        battery_cat = self.env['product.category'].search([('name', '=', "Storage")], limit=1)
        micro_cat = self.env['product.category'].search([('name', '=', "Micro Inverters")], limit=1)
        inverter_cat = self.env['product.category'].search([('name', '=', "Inverters")], limit=1)
        panel_cat = self.env['product.category'].search([('name', '=', "Solar Panels")], limit=1)

        cat_ids = self.env['product.category'].search(['|', '|', '|',
            ('id', 'child_of', battery_cat.id),
            ('id', 'child_of', micro_cat.id),
            ('id', 'child_of', inverter_cat.id),
            ('id', 'child_of', panel_cat.id)
        ]).ids

        if self.categ_id and self.categ_id.id in cat_ids:
            return True
        return False
