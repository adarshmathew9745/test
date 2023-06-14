# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Employee Loan',
    'author': 'Adarsh',
    'sequence': -100,
    'version': '1.0.0',
    'category': 'Task',
    'summary': 'Loan management system',
    'description': """Loan management system software""",
    'depends': ['hr', 'base', 'website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/loan_action.xml',
        'views/res_config_settings_views.xml',
        'views/website_form.xml',
        'views/website_form_tree.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
