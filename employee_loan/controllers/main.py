from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.utils
from odoo.http import request
from datetime import date
import json


class LoanCreate(http.Controller):
    @http.route('/loan_webform', type='http', auth="user", website=True)
    def render_template(self, **kw):
        employee_rec = request.env['loan.approval']
        if request.env.user.has_group('base.group_portal'):
            loan_data = employee_rec.search([('employee_id', '=', request.env.user.employee_id.id)])
        else:
            loan_data = employee_rec.search([])
        vals = {'loans': loan_data, 'page_name': 'loan_list_view'}
        return request.render('employee_loan.loan_list_view', vals)

    @http.route('/loan_request', type='http', auth="user", website=True)
    def render_request_loan(self, **kw):
        if request.env.user.has_group('base.group_portal'):
            data = request.env.user.employee_id
            return request.render('employee_loan.create_loan', {
                'data': data,
                'date': date.today(),
                'company_rec': request.env.company,
            })
        else:
            employee_rec = request.env['hr.employee'].sudo().search([])
            department_rec = request.env['hr.department'].sudo().search([])
            job_rec = request.env['hr.job'].sudo().search([])
        return request.render('employee_loan.create_loan', {
            'employee_rec': employee_rec,
            'department_rec': department_rec,
            'job_rec': job_rec,
            'date': date.today(),
            'company_rec': request.env.company,
        })

    @http.route('/webloan', type='http', auth="user", website=True)
    def create_webloan(self, **kw):
        loan = request.env['loan.approval'].sudo().create(kw)
        if request.env.user.sudo().has_group('base.group_portal'):
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            quotation_link = '<a href="%s/web#id=%d&model=%s&view_type=%s" style="background-color: #875A7B; padding: 8px 32px 8px 32px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">New Loan Approval</a>' % (
                base_url, loan.id, 'loan.approval', 'form')
            body_html = quotation_link
            channel = request.env['mail.channel'].sudo().channel_get(
                [request.env.user.employee_id.parent_id.sudo().user_id.partner_id.id])
            channel_id = request.env['mail.channel'].browse(channel["id"])
            channel_id.message_post(
                body=body_html,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )
        return request.render('employee_loan.loan_create_thanks', {})

    def _prepare_home_portal_values(self, counters):
        values = super(LoanCreate, self)._prepare_home_portal_values(counters)
        values['loan_counters'] = request.env['loan.approval'].search_count([])
        return values

    @http.route('/my/loan', type='http', auth="user", website=True)
    def create_webloanlist(self, **kw):
        employee_rec = request.env['loan.approval']
        if request.env.user.has_group('base.group_portal'):
            loan_data = employee_rec.search([('employee_id', '=', request.env.user.employee_id.id)])
        else:
            loan_data = employee_rec.search([])
        vals = {'loans': loan_data, 'page_name': 'loan_list_view'}
        return request.render('employee_loan.loan_list_view', vals)

    @http.route(['/my/loan/<model("loan.approval"):employee_id>'], type='http', auth="user", website=True)
    def create_webloanlistFormView(self, employee_id, **kw):
        loans = employee_id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        quotation_link = '%s/web#id=%d&model=%s&view_type=%s' % (
            base_url, loans.id, 'loan.approval', 'form')
        if request.env.user.has_group('base.group_portal'):
            return request.render('employee_loan.create_loan', {'loans': loans, 'quotation_link': quotation_link, })
        else:
            return werkzeug.utils.redirect(quotation_link)

    @http.route(['/loan_webform/ajax/work'],
                type='http', auth='user', website=True)
    def onchange_fields_in_portal(self, **post):
        emp_name_list = post.get('emp_name_list')
        if emp_name_list:
            employee = request.env['hr.employee'].sudo().search([('id', '=', int(emp_name_list))])
            emp_list = []
            emp_job = []
            for emp in employee:
                emp_list.append({'id': emp.department_id.id,
                                 'department_id': emp.department_id.name,
                                 })
                emp_job.append({'id': emp.job_id.id,
                                'job_id': emp.job_id.name,
                                })
            data_dict = {
                'employee': emp_list,
                'job': emp_job,
            }
        return json.JSONEncoder().encode(data_dict)

    @http.route('/loan_request/amount', type='http', auth="user", website=True)
    def onchange_loan_amount(self, **post):
        emp_loan_amount = post.get('emp_loan_amount')
        limit = request.env['ir.config_parameter'].sudo().get_param('employee_loan.loan_limit')
        return json.JSONEncoder().encode(limit)


class LoanCreatelist(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(LoanCreatelist, self)._prepare_home_portal_values(counters)
        if request.env.user.has_group('base.group_portal'):
            values['loan_counters'] = request.env['loan.approval'].search_count(
                [('employee_id', '=', request.env.user.employee_id.id)])
            return values

        else:
            values['loan_counters'] = request.env['loan.approval'].search_count([])
            return values
