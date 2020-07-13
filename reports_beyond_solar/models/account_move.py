from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_install_date(self):
        self.ensure_one()
        projects = self.mapped('invoice_line_ids.sale_line_ids.task_id')
        if projects:
            return projects.filtered(lambda p: p.planned_date_begin)[:1].planned_date_begin or 'Upon Installation'
        return self.invoice_date_due
