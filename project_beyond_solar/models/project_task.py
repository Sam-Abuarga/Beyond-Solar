from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    calendar_date_begin = fields.Datetime(string="Calendar Date Start", compute='_compute_calendar_begin', inverse='_set_calendar_begin', store=True)
    calendar_date_end = fields.Datetime(string="Calendar Date End", compute='_compute_calendar_end', inverse='_set_calendar_end', store=True)

    install_status = fields.Selection(string="Status", required=True, default='pending', copy=False, selection=lambda self: [
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
    date_worksheet_start = fields.Datetime(string="Worksheets Started", copy=False)
    date_worksheet_check = fields.Datetime(string="In House Check Completed", copy=False)
    date_worksheet_swms = fields.Datetime(string="SWMS Completed", copy=False)
    date_worksheet_site = fields.Datetime(string="Site Condition Completed", copy=False)
    date_worksheet_client_signature = fields.Datetime(string="Client Signature Completed", copy=False)
    date_worksheet_install = fields.Datetime(string="Installation and Commissioning Completed", copy=False)
    date_worksheet_handover = fields.Datetime(string="Handover Completed", copy=False)
    date_worksheet_finish = fields.Datetime(string="Worksheets Finished", copy=False)

    has_preexisting_issues = fields.Boolean(string="Roof Has Pre-Existing Issues", copy=False)
    has_variation = fields.Boolean(string="Has Panel Variations", copy=False)
    variation_description = fields.Text(string="Panel Variations", copy=False)
    additional_swms = fields.Text(string="Additional Site-Specific Requirements", copy=False)
    recommended_swms = fields.Text(string="Recommendations for Improvements to This Document", copy=False)

    modules_in_string = fields.Integer(string="Modules in Series in a String", copy=False)
    strings_in_parallel = fields.Integer(string="Strings in Parallel in PV Array", copy=False)
    inverter_count = fields.Integer(string="Number of Inverters", compute='_compute_inverter_count')
    mppt_count = fields.Integer(string="Number of MPPTs", copy=False)

    customer_name = fields.Char(string="Customer Signature Name", copy=False)
    customer_signature = fields.Char(string="Customer Signature", copy=False)

    pv_details = fields.Char(string="PV Details", compute='_compute_sale_details')
    inv_details = fields.Char(string="Inverter Details", compute='_compute_sale_details')

    swms_signature_ids = fields.Many2many(comodel_name='ir.attachment', string="SWMS Signatures", copy=False)
    swms_signature_names = fields.Text(string="SWMS Signatures Names", readonly=1, copy=False)

    install_notes = fields.Text(string="Installation Notes", copy=False)
    install_signature = fields.Binary(string="Installation Signature", copy=False)
    install_signed_by = fields.Char(string="Installation Signature Name", copy=False)
    install_saved = fields.Boolean(string="Installation Saved", copy=False)

    install_array_frame = fields.Boolean(string="Installation Array Frame")
    install_array_install = fields.Boolean(string="Installation Array Installation")
    install_array_dissimilar = fields.Boolean(string="Installation Array Dissimilar Metals")
    install_array_penetrations = fields.Boolean(string="Installation Array Penetrations")
    install_array_losses = fields.Boolean(string="Installation Array Wiring Losses")
    install_array_protection = fields.Boolean(string="Installation Array String Protection")
    install_array_mechanical = fields.Boolean(string="Installation Array Mechanical Damage")
    install_array_weatherproof = fields.Boolean(string="Installation Array Weatherproof Isolator")
    install_acdc_install = fields.Boolean(string="Installation LV DC & AC Installed")
    install_acdc_tested = fields.Boolean(string="Installation LV DC & AC Tested")
    install_inverter_pv_isolator = fields.Boolean(string="Installation Inverter PV Isolator")
    install_inverter_ac_isolator = fields.Boolean(string="Installation Inverter AC Isolator")
    install_inverter_breaker = fields.Boolean(string="Installation Inverter Circuit Breaker")
    install_inverter_install = fields.Boolean(string="Installation Inverter Installed")
    install_inverter_power = fields.Boolean(string="Installation Inverter Mains Loss")
    install_inverter_resume = fields.Boolean(string="Installation Inverter Resume")

    s1_polarity = fields.Char(string="String 1 Polarity", copy=False)
    s1_voltage = fields.Float(string="String 1 Voltage", copy=False)
    s1_short_circuit = fields.Float(string="String 1 Short Circuit", copy=False)
    s1_operating_current = fields.Float(string="String 1 Operating Current", copy=False)
    s2_polarity = fields.Char(string="String 2 Polarity", copy=False)
    s2_voltage = fields.Float(string="String 2 Voltage", copy=False)
    s2_short_circuit = fields.Float(string="String 2 Short Circuit", copy=False)
    s2_operating_current = fields.Float(string="String 2 Operating Current", copy=False)
    s3_polarity = fields.Char(string="String 3 Polarity", copy=False)
    s3_voltage = fields.Float(string="String 3 Voltage", copy=False)
    s3_short_circuit = fields.Float(string="String 3 Short Circuit", copy=False)
    s3_operating_current = fields.Float(string="String 3 Operating Current", copy=False)
    s4_polarity = fields.Char(string="String 4 Polarity", copy=False)
    s4_voltage = fields.Float(string="String 4 Voltage", copy=False)
    s4_short_circuit = fields.Float(string="String 4 Short Circuit", copy=False)
    s4_operating_current = fields.Float(string="String 4 Operating Current", copy=False)
    tot_voltage = fields.Float(string="Total Voltage", copy=False)
    positive_resistance = fields.Float(string="Array Positive to Earth", copy=False)
    negative_resistance = fields.Float(string="Array Negative to Earth", copy=False)

    show_submit_install = fields.Boolean(string="Show Installation Submit", compute='_compute_show_submit_install')
    show_all_install = fields.Boolean(string="Show All Installation Fields", compute='_compute_show_all_install')

    def _compute_show_all_install(self):
        for rec in self:
            if "Replacement" in rec.project_id.name and not rec.has_battery and not rec.has_panel:
                rec.show_all_install = False
            else:
                rec.show_all_install = True

    def _compute_show_submit_install(self):
        for rec in self:
            if rec.show_all_install:
                rec.show_submit_install = rec.install_saved and not rec.date_worksheet_install and all([
                    rec.tot_voltage,
                    rec.positive_resistance,
                    rec.negative_resistance,
                    rec.install_array_frame,
                    rec.install_array_install,
                    rec.install_array_dissimilar,
                    rec.install_array_penetrations,
                    rec.install_array_losses,
                    rec.install_array_protection,
                    rec.install_array_mechanical,
                    rec.install_array_weatherproof,
                    rec.install_acdc_install,
                    rec.install_acdc_tested,
                    rec.install_inverter_pv_isolator,
                    rec.install_inverter_breaker,
                    rec.install_inverter_install,
                    rec.install_inverter_power,
                    rec.install_inverter_resume
                ])
            else:
                rec.show_submit_install = rec.install_saved and not rec.date_worksheet_install and all([
                    rec.install_acdc_install,
                    rec.install_acdc_tested,
                    rec.install_inverter_pv_isolator,
                    rec.install_inverter_breaker,
                    rec.install_inverter_install,
                    rec.install_inverter_power,
                    rec.install_inverter_resume
                ])

    @api.depends('planned_date_begin', 'x_studio_proposed_date')
    def _compute_calendar_begin(self):
        for rec in self:
            rec.calendar_date_begin = rec.planned_date_begin or rec.x_studio_proposed_date

    @api.depends('planned_date_end', 'x_studio_proposed_end_date')
    def _compute_calendar_end(self):
        for rec in self:
            rec.calendar_date_end = rec.planned_date_end or rec.x_studio_proposed_end_date

    def _set_calendar_begin(self):
        for rec in self:
            if rec.planned_date_begin:
                rec.planned_date_begin = rec.calendar_date_begin
            else:
                rec.x_studio_proposed_date = rec.calendar_date_begin

    def _set_calendar_end(self):
        for rec in self:
            if rec.planned_date_end:
                rec.planned_date_end = rec.calendar_date_end
            else:
                rec.x_studio_proposed_end_date = rec.calendar_date_end

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

    def _compute_inverter_count(self):
        inverter_cat = self.env['product.category'].search([('name', '=', "Inverters")], limit=1)
        inverter_cat_ids = self.env['product.category'].search([('id', 'child_of', inverter_cat.id)]).ids

        for rec in self:
            rec.inverter_count = len(rec.sale_order_id.order_line.filtered(lambda l: l.product_id.categ_id.id in inverter_cat_ids))

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

    def get_formview_id(self, access_uid=None):
        return self.env.ref('project_beyond_solar.project_task_simplified_form_view').id

    def action_email_installation(self):
        ctx = dict(
            default_use_template=True,
            default_template_id=self.env.ref('project_beyond_solar.mail_template_project_task_installation').id,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': ctx
        }

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if order == 'create_date desc':
            order = 'calendar_date_begin'
        elif order == 'project_id, create_date desc':
            order = 'project_id, calendar_date_begin'
        return super(ProjectTask, self).search(args, offset, limit, order, count)
