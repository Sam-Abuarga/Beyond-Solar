from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from datetime import datetime
import time


class Task(CustomerPortal):
    @http.route('/my/task/<int:id>/start', type='http', auth='user', website=True)
    def task_start(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_start = datetime.now()
        task.install_status = 'progress'

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/reschedule', type='http', auth='user', website=True)
    def task_reschedule(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.install_status = 'rescheduled'
        task.user_id = task.project_id.user_id
        task.message_post(body=f"Task rescheduled. Reason: {kwargs.get('reason','')}", message_type="comment", subtype="mail.mt_note")

        return request.redirect('/my/tasks')

    @http.route('/my/task/<int:id>/incomplete', type='http', auth='user', website=True)
    def task_incomplete(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.install_status = 'incomplete'
        task.user_id = task.project_id.user_id
        task.message_post(body=f"Task marked incomplete. Reason: {kwargs.get('reason','')}", message_type="comment", subtype="mail.mt_note")

        return request.redirect('/my/tasks')

    @http.route('/my/task/<int:id>/worksheet/check', type='http', auth='user', website=True)
    def task_worksheet_check(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_check = datetime.now()

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/check/signature', type='json', website=True)
    def task_worksheet_check_signature(self, id, name=None, signature=None, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.customer_name = name
        task.customer_signature = signature
        task.date_worksheet_client_signature = datetime.now()

        return {
            'force_refresh': True,
        }

    @http.route('/my/task/<int:id>/worksheet/swms', type='http', auth='user', website=True)
    def task_worksheet_swms(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_swms = datetime.now()

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/swms/save', type='http', auth='user', website=True)
    def task_worksheet_swms_save(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        if 'additional_swms' in kwargs:
            task.additional_swms = kwargs['additional_swms']
        if 'recommended_swms' in kwargs:
            task.recommended_swms = kwargs['recommended_swms']

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/swms/signature', type='json', website=True)
    def task_worksheet_swms_signature(self, id, name=None, signature=None, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        name = name or request.env.user.name

        if not task.swms_signature_names:
            task.swms_signature_names = name
        else:
            task.swms_signature_names += "\n" + name

        task.swms_signature_ids += request.env['ir.attachment'].sudo().create({
            'datas': signature,
            'name': name + '.png',
        })

        return {
            'force_refresh': True,
        }

    @http.route('/my/task/<int:id>/worksheet/site', type='http', auth='user', website=True)
    def task_worksheet_site(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_site = datetime.now()
        if 'existing_issues' in kwargs:
            task.has_preexisting_issues = True
        if 'variations' in kwargs:
            task.has_variation = True
        if 'variation_description' in kwargs:
            task.variation_description = kwargs['variation_description']

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/install', type='http', auth='user', website=True)
    def task_worksheet_install(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        fields = {
            'array_1_azimuth': 'x_studio_array_1_azimuth',
            'array_2_azimuth': 'x_studio_array_2_azimuth',
            'array_3_azimuth': 'x_studio_array_3_azimuth',
            'array_4_azimuth': 'x_studio_array_4_azimuth',
            'array_1_count': 'x_studio_array_1_number_of_panels',
            'array_2_count': 'x_studio_array_2_number_of_panels',
            'array_3_count': 'x_studio_array_3_number_of_panels',
            'array_4_count': 'x_studio_array_4_number_of_panels',
            's1_polarity': 's1_polarity',
            's2_polarity': 's2_polarity',
            's3_polarity': 's3_polarity',
            's4_polarity': 's4_polarity',
            'modules_in_string': 'modules_in_string',
            'strings_in_parallel': 'strings_in_parallel',
            'inverter_count': 'inverter_count',
            'mppt_count': 'mppt_count',
            'install_notes': 'install_notes'
        }

        boolean_fields = {
            'certified': 'install_array_frame',
            'manufacturer': 'install_array_install',
            'metals': 'install_array_dissimilar',
            'weatherproof': 'install_array_penetrations',
            'current': 'install_array_losses',
            'protection': 'install_array_protection',
            'supported': 'install_array_mechanical',
            'mounted': 'install_array_weatherproof',
            'installed_electrician': 'install_acdc_install',
            'tested_electrician': 'install_acdc_tested',
            'isolator': 'install_inverter_pv_isolator',
            'isolator_output': 'install_inverter_ac_isolator',
            'breaker': 'install_inverter_breaker',
            'inverter_manufacturer': 'install_inverter_install',
            'inverter_loss': 'install_inverter_power',
            'inverter_delay': 'install_inverter_resume',
        }

        float_fields = {
            's1_voltage': 's1_voltage',
            's1_short_circuit': 's1_short_circuit',
            's1_operating_current': 's1_operating_current',
            's2_voltage': 's2_voltage',
            's2_short_circuit': 's2_short_circuit',
            's2_operating_current': 's2_operating_current',
            's3_voltage': 's3_voltage',
            's3_short_circuit': 's3_short_circuit',
            's3_operating_current': 's3_operating_current',
            's4_voltage': 's4_voltage',
            's4_short_circuit': 's4_short_circuit',
            's4_operating_current': 's4_operating_current',
            'tot_voltage': 'tot_voltage',
            'positive_resistance': 'positive_resistance',
            'negative_resistance': 'negative_resistance',
            'array_1_tilt': 'x_studio_array_1_tilt_angle',
            'array_2_tilt': 'x_studio_array_2_tilt_angle',
            'array_3_tilt': 'x_studio_array_3_tilt_angle',
            'array_4_tilt': 'x_studio_array_4_tilt_angle',
        }
        for field in fields:
            if field in kwargs:
                task[fields[field]] = kwargs[field]

        for field in boolean_fields:
            task[boolean_fields[field]] = field in kwargs

        for field in float_fields:
            if field in kwargs:
                task[float_fields[field]] = float(kwargs[field] or 0)

        task.install_saved = True

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/install/signature', type='json', website=True)
    def task_worksheet_install_signature(self, id, name=None, signature=None, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.write({
            'date_worksheet_install': datetime.now(),
            'install_signed_by': name or request.env.user.name,
            'install_signature': signature,
        })

        return {
            'force_refresh': True,
        }

    @http.route('/my/task/<int:id>/worksheet/handover', type='http', auth='user', website=True)
    def task_worksheet_handover(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_handover = datetime.now()
        task.date_worksheet_finish = datetime.now()
        task.install_status = 'done'

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')
