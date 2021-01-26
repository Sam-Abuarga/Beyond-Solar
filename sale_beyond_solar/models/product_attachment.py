from odoo import api, fields, models


class ProductAttachment(models.Model):
    _name = 'product.attachment'
    _description = "Product Attachment"

    name = fields.Char(string="Name", required=True)
    file = fields.Binary(string="Attachment", required=True, attachment=True)
    filename = fields.Char(string="Attachment Filename", required=True)
    type = fields.Selection(string="Attachment Type", required=True, selection=[
        ('warranty', "Warranty"),
        ('datasheet', "Datasheet"),
    ])

    @api.onchange('filename')
    def _onchange_filename(self):
        if self.filename and not self.name:
            self.name = self.filename.split('.')[0]
