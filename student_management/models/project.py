from odoo import api, models, fields, _
from lxml import etree, html
import json

class ProjectFormView(models.Model):
    _name = 'project.create'
    _description = 'Project Create'

    name = fields.Char(string='Student Name', required=True)
    phone = fields.Char(string="Phone")
    reference_no = fields.Char(string='Order Reference', required=True,
                               readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('completed', 'Completed')
    ], string='Status', readonly=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department')
    date = fields.Date(string='Date')
    company_id = fields.Many2one('res.company', string='Company')
    # installment_line_ids = fields.One2many('loan.installment.lines', 'parent_id', string='Installment Lines',
    #                                        auto_join=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'student.order') or _('New')
        res = super(ProjectFormView, self).create(vals)
        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.company_id = self.env.company
        self.date = fields.Datetime.today()

