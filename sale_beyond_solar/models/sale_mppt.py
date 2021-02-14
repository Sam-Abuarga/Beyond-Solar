from odoo import api, fields, models


class SaleMppt(models.Model):
    _name = 'sale.mppt'
    _description = "Sale MPPT"
    _order = 'sale_line_id,sale_line_index,header desc,mppt_id'

    name = fields.Char(string="Name", required=True)

    sale_id = fields.Many2one(comodel_name='sale.order', string="Sale", required=True, ondelete='cascade')
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string="Sale Line", required=True, ondelete='cascade')
    sale_line_index = fields.Integer(string="Sale Line Index")
    mppt_id = fields.Many2one(comodel_name='product.mppt', string="MPPT", ondelete='cascade')
    header = fields.Boolean(string="Header", compute='_compute_header', store=True)

    panel_count = fields.Integer(string="# of Panels")
    azimuth_angle = fields.Float(string="Azimuth Angle")
    tilt_angle = fields.Float(string="Tile Angle")
    notes = fields.Text(string="Notes")

    panel_count_valid = fields.Integer(string="# of Panels")
    azimuth_angle_valid = fields.Float(string="Azimuth Angle")
    tilt_angle_valid = fields.Float(string="Tile Angle")
    notes_valid = fields.Text(string="Notes")

    @api.depends('mppt_id')
    def _compute_header(self):
        for rec in self:
            rec.header = not rec.mppt_id

    @api.model
    def create(self, vals):
        for field in ['panel_count', 'azimuth_angle', 'tilt_angle', 'notes']:
            if field in vals:
                vals[field + '_valid'] = vals[field]
        return super(SaleMppt, self).create(vals)

    def write(self, vals):
        sales = self.filtered(lambda m: m.sale_id.state in ['sale', 'lock'])
        res = super(SaleMppt, sales).write(vals)
        quotes = self - sales
        if not quotes:
            return res
        for field in ['panel_count', 'azimuth_angle', 'tilt_angle', 'notes']:
            if field in vals:
                vals[field + '_valid'] = vals[field]
        return super(SaleMppt, quotes).write(vals)
