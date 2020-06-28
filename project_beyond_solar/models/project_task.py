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

    modules_in_string = fields.Integer(string="Modules in Series in a String")
    strings_in_parallel = fields.Integer(string="Strings in Parallel in PV Array")
    inverter_count = fields.Integer(string="Number of Inverters")
    mppt_count = fields.Integer(string="Number of MPPTs")

    customer_name = fields.Char(string="Customer Signature Name")
    customer_signature = fields.Char(string="Customer Signature")

    pv_details = fields.Char(string="PV Details", compute='_compute_sale_details')
    inv_details = fields.Char(string="Inverter Details", compute='_compute_sale_details')

    swms_signature_ids = fields.Many2many(comodel_name='ir.attachment', string="Signatures")
    swms_signature_names = fields.Text(string="Current Signatures", readonly=1)

    install_notes = fields.Text(string="Installation Notes")
    install_signature = fields.Binary(string="Installation Signature")
    install_signed_by = fields.Char(string="Installation Signature Name")
    install_saved = fields.Boolean(string="Installation Saved")

    s1_polarity = fields.Char(string="String 1 Polarity")
    s1_voltage = fields.Float(string="String 1 Voltage")
    s1_short_circuit = fields.Float(string="String 1 Short Circuit")
    s1_operating_current = fields.Float(string="String 1 Operating Current")
    s2_polarity = fields.Char(string="String 2 Polarity")
    s2_voltage = fields.Float(string="String 2 Voltage")
    s2_short_circuit = fields.Float(string="String 2 Short Circuit")
    s2_operating_current = fields.Float(string="String 2 Operating Current")
    s3_polarity = fields.Char(string="String 3 Polarity")
    s3_voltage = fields.Float(string="String 3 Voltage")
    s3_short_circuit = fields.Float(string="String 3 Short Circuit")
    s3_operating_current = fields.Float(string="String 3 Operating Current")
    s4_polarity = fields.Char(string="String 4 Polarity")
    s4_voltage = fields.Float(string="String 4 Voltage")
    s4_short_circuit = fields.Float(string="String 4 Short Circuit")
    s4_operating_current = fields.Float(string="String 4 Operating Current")
    tot_voltage = fields.Float(string="Total Voltage")
    positive_resistance = fields.Float(string="Array Positive to Earth")
    negative_resistance = fields.Float(string="Array Negative to Earth")

    def _compute_sale_details(self):
        inverter_cat = self.env['product.category'].search([('name', '=', "Inverters")], limit=1)
        panel_cat = self.env['product.category'].search([('name', '=', "Solar Panels")], limit=1)

        inverter_cat_ids = self.env['product.category'].search([('id', 'child_of', inverter_cat.id)]).ids
        panel_cat_ids = self.env['product.category'].search([('id', 'child_of', panel_cat.id)]).ids

        for rec in self:
            inverter = False
            panel = False

            for line in rec.x_studio_product_list.filtered(lambda l: not l.display_type):
                id = line.product_id.categ_id.id
                if id in inverter_cat_ids:
                    inverter = line.product_id
                if id in panel_cat_ids:
                    panel = line.product_id

            if panel:
                rec.pv_details = panel.name
            else:
                rec.pv_details = ''
            if inverter:
                rec.inv_details = inverter.name
            else:
                rec.inv_details = ''

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
