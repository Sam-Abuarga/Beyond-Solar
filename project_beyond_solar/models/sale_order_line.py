from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        if project.sequence_id:
            res['name'] = project.sequence_id._next() + ' - ' + self.order_id.partner_id.name
        return res
