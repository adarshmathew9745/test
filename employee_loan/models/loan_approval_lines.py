from odoo import api, fields, models, _


class loaninstallmenlines(models.Model):
    _name = 'loan.installment.lines'
    _description = 'Loan Approval'

    parent_id = fields.Many2one('loan.approval', string="Parent Id", readonly=True)
    date = fields.Date(string='Payment Date', readonly=True)
    loan_amount = fields.Float(string='Amount', readonly=True)




