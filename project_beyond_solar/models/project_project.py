from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sequence_id = fields.Many2one(comodel_name='ir.sequence', string="Task Sequence")
