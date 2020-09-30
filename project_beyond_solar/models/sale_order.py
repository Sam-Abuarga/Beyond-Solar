from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tasks_ids = fields.Many2many('project.task', compute='_compute_tasks_ids', string='Tasks associated to this sale', store=True)
    tasks_count = fields.Integer(string='Tasks', compute='_compute_task_count', groups="project.group_project_user", store=True)

    @api.depends('order_line.task_id')
    def _compute_tasks_ids(self):
        for rec in self:
            rec.tasks_ids = rec.mapped('order_line.task_id')

    @api.depends('tasks_ids')
    def _compute_task_count(self):
        for rec in self:
            rec.tasks_count = len(rec.tasks_ids)
