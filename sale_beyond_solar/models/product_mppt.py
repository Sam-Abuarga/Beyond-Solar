from odoo import api, fields, models


class ProductMppt(models.Model):
    _name = 'product.mppt'
    _description = "Product MPPT"
    _order = 'mppt_number, input_number'

    name = fields.Char(string="String", compute='_compute_name', store=True)
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string="Product", required=True)

    mppt_number = fields.Integer(string="MPPT Number")
    input_number = fields.Integer(string="MPPT Number")
    enabled = fields.Boolean(string="Enabled", default=True)

    @api.depends('mppt_number', 'input_number')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{chr(rec.mppt_number + 65)}{rec.input_number + 1}"
