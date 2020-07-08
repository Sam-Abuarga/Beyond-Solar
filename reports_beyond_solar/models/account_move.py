from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_install_date(self):
        self.ensure_one()
        projects = self.mapped('invoice_line_ids.sale_line_ids.task_id').filtered(lambda p: p.planned_date_begin or p.x_studio_proposed_date)
        if projects:
            return projects[0].planned_date_begin or projects[0].x_studio_proposed_date
        return self.invoice_date_due
