from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    install_status = fields.Selection(string="Status", required=True, default='pending', selection=lambda self: [
        ('pending', "Pending"),
        ('progress', "In Progress"),
        ('done', "Installation Complete"),
        ('incomplete', "Incomplete"),
        ('rescheduled', "Rescheduled"),
    ])
    job_status = fields.Selection(string="Job Status", compute='_compute_job_status', selection=[
        ('draft', "Not Ready"),
        ('ready', "Ready to Book"),
        ('booked', "Booked"),
        ('done', "Done"),
    ])
    date_worksheet_start = fields.Datetime(string="Worksheets Started")
    date_worksheet_check = fields.Datetime(string="In House Check Completed")
    date_worksheet_swms = fields.Datetime(string="SWMS Completed")
    date_worksheet_site = fields.Datetime(string="Site Condition Completed")
    date_worksheet_install = fields.Datetime(string="Installation and Commissioning Completed")
    date_worksheet_handover = fields.Datetime(string="Handover Completed")
    date_worksheet_finish = fields.Datetime(string="Worksheets Finished")

    has_preexisting_issues = fields.Boolean(string="Roof Has Pre-Existing Issues")
    has_variation = fields.Boolean(string="Has Panel Variations")
    variation_description = fields.Text(string="Panel Variations")
    additional_swms = fields.Text(string="Additional Site-Specific Requirements")
    recommended_swms = fields.Text(string="Recommendations for Improvements to This Document")

    def _compute_job_status(self):
        for rec in self:
            if rec.x_studio_installation_completed:
                rec.job_status = 'done'
            elif rec.x_studio_booked_for_installation:
                rec.job_status = 'booked'
            elif rec.x_studio_ready_for_booking:
                rec.job_status = 'ready'
            else:
                rec.job_status = 'draft'

    def get_status(self):
        self.ensure_one()
        return self.status_mapping[self.status or 'pending']

    def get_start_date(self):
        self.ensure_one()
        if self.planned_date_begin:
            return f"{self.planned_date_begin:%a %d/%m/%Y}"
        return "-"

    def get_end_date(self):
        self.ensure_one()
        if self.planned_date_end:
            return f"{self.planned_date_end:%a %d/%m/%Y}"
        return "-"

    def action_copy_proposed(self):
        for rec in self:
            vals = {}
            if rec.x_studio_proposed_team.user_id:
                vals['user_id'] = rec.x_studio_proposed_team.user_id
            if rec.x_studio_proposed_date:
                vals['planned_date_begin'] = rec.x_studio_proposed_date
            if rec.x_studio_proposed_end_date:
                vals['planned_date_end'] = rec.x_studio_proposed_end_date
            if vals:
                rec.write(vals)
