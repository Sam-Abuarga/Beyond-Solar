from odoo import api, fields, models


class ConnectionDiagram(models.Model):
    _name = 'connection.diagram'
    _description = "Connection Diagram"
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Name")
    line_ids = fields.One2many(comodel_name='connection.diagram.criteria', inverse_name='diagram_id', string="Criteria")

    pdf_attachment = fields.Binary(string="PDF Attachment", attachment=True, required=True)
    pdf_name = fields.Char(string="PDF Filename")
