# -*- coding: utf-8 -*
{
    'name': 'Student Registration',
    'author': 'Adarsh',
    'sequence': -1,
    'version': '15.0.00',
    'category': '',
    'summary': 'Student Registration system',
    'description': """Student Registration system software""",
    'depends': ['base', 'sale', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_form_view.xml',
        'views/menu.xml',
        'views/sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
