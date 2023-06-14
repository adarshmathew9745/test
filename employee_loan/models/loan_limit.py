from odoo import api, fields, models, _
from lxml import etree
import json
from datetime import date
from datetime import timedelta
from odoo.exceptions import UserError


class ResConfigsettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    loan_limit = fields.Float(string='Loan Maximum Limit', config_parameter='employee_loan.loan_limit')


class LoanApproval(models.Model):
    _name = 'loan.approval'
    _description = 'Loan Approval'
    _rec_name = 'reference_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference_no = fields.Char(string='Order Reference', required=True,
                               readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approve', 'Approve'),
        ('refuse', 'Refuse'),
        ('cancel', 'Cancel')
    ], string='Status', readonly=True, tracking=True, default='draft', )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_image = fields.Image(related='employee_id.image_1920', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    loan_amount = fields.Float(string='Loan Amount', required=True)
    payment_start_date = fields.Date(string='Payment Start Date', required=True)
    company_currency_id = fields.Many2one("res.currency", string='Currency')
    date = fields.Date(string='Date')
    job_position_id = fields.Many2one('hr.job', string='Job Position')
    no_of_installment = fields.Integer(string='No Of Installment')
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Test Button', compute='_compute_active', readonly=True, invisible=True)
    active_bool = fields.Boolean(string='Test Button', readonly=True, invisible=True)
    active_bool1 = fields.Boolean(string='Test Button', readonly=True, invisible=True)
    installment_line_ids = fields.One2many('loan.installment.lines', 'parent_id', string='Installment Lines',
                                           auto_join=True)

    def write(self, vals):
        res = super(LoanApproval, self).write(vals)
        if self.state == 'approve':
            fields_changed = {}
            for field_name in vals:
                field_value = vals[field_name]
                if self[field_name] != field_value:
                    fields_changed[field_name] = self[field_name]
            if fields_changed:
                self.write({'state': 'draft'})
        return res

    @api.onchange('loan_amount')
    def onchange_loan_limit(self):
        limit = self.env['ir.config_parameter'].sudo().get_param('employee_loan.loan_limit')
        if float(limit) < self.loan_amount:
            raise UserError(_("Maximum Loan Amount %s!" % (limit,)))

    @api.depends('employee_id')
    def _compute_active(self):
        for rec in self:
            if self.env.user.has_group('hr.group_hr_manager'):
                rec.active = True
        else:
            rec.active = False

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'loan.order') or _('New')
        res = super(LoanApproval, self).create(vals)
        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.department_id = self.employee_id.department_id
        self.job_position_id = self.employee_id.job_id
        self.company_currency_id = self.env.company.currency_id.id
        self.company_id = self.env.company
        self.date = fields.Datetime.today()

    def compute_installment(self):
        if not self.loan_amount or not self.no_of_installment:
            raise UserError(_("Please fill the required fields!"))
        today = date.today()
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        amount = self.loan_amount
        num_installments = float(self.no_of_installment)
        installment_lines = [(5, 0, 0)]
        for i in range(self.no_of_installment):
            if i == 0:
                installment_line = (0, 0, {
                    'parent_id': self.id,
                    'date': self.payment_start_date,
                    'loan_amount': amount / num_installments,
                })
            else:
                installment_date = next_month + timedelta(days=30 * i)
                installment_line = (0, 0, {
                    'parent_id': self.id,
                    'date': installment_date.replace(day=1),
                    'loan_amount': amount / num_installments,
                })
            installment_lines.append(installment_line)
            self.installment_line_ids = installment_lines

    def state_submitted(self):
        if not self.installment_line_ids:
            raise UserError(_("Compute Installments!"))
        else:
            self.state = 'submitted'
            self.active_bool = True
            if not self.env.user.has_group('hr.group_hr_manager'):
                body_html = 'New Loan Approval NO:%s' % (self.reference_no,)
                channel = self.env['mail.channel'].sudo().channel_get(
                    [self.env.user.employee_id.parent_id.user_id.partner_id.id])
                channel_id = self.env['mail.channel'].browse(channel["id"])
                channel_id.message_post(
                    body=body_html,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )

    def cancel_loan(self):
        self.state = 'cancel'

    def approve_loan(self):
        limit = self.env['ir.config_parameter'].sudo().get_param('employee_loan.loan_limit')
        if float(limit) > float(self.loan_amount):
            self.state = 'approve'

    def refuse_loan(self):
        self.state = 'refuse'

    def set_to_draft(self):
        self.state = 'draft'

    def approve(self):
        self.state = 'approve'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(LoanApproval, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                modifiers = json.loads(node.get("modifiers"))
                if 'readonly' not in modifiers:
                    modifiers['readonly'] = [['state', '=', 'submitted']]
                else:
                    if type(modifiers['readonly']) != bool:
                        modifiers['readonly'].insert(0, '|')
                        modifiers['readonly'] += [['state', '=', 'submitted']]
                node.set("modifiers", json.dumps(modifiers))
                res['arch'] = etree.tostring(doc)
        return res


