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
        task.status = 'progress'

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/reschedule', type='http', auth='user', website=True)
    def task_reschedule(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.status = 'rescheduled'
        task.user_id = task.project_id.user_id
        task.message_post(body=f"Task rescheduled. Reason: {kwargs.get('reason','')}", message_type="comment", subtype="mail.mt_note")

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/incomplete', type='http', auth='user', website=True)
    def task_incomplete(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.status = 'incomplete'
        task.user_id = task.project_id.user_id
        task.message_post(body=f"Task marked incomplete. Reason: {kwargs.get('reason','')}", message_type="comment", subtype="mail.mt_note")

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/finish', type='http', auth='user', website=True)
    def task_finish(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_finish = datetime.now()
        task.status = 'done'

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/check', type='http', auth='user', website=True)
    def task_worksheet_check(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_check = datetime.now()

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/swms', type='http', auth='user', website=True)
    def task_worksheet_swms(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_swms = datetime.now()

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

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

        task.date_worksheet_install = datetime.now()

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')

    @http.route('/my/task/<int:id>/worksheet/handover', type='http', auth='user', website=True)
    def task_worksheet_handover(self, id, **kwargs):
        task = request.env['project.task'].browse(id)
        if not task.exists():
            return http.request.not_found()

        task.date_worksheet_handover = datetime.now()

        return request.redirect(f'/my/task/{id}#worksheets?t={int(time.time())}')
