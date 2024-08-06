{
    'name': 'Partner Email Validation',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Adds email verification for contacts',
    'depends': ['base', 'mail'],
    'data': [
        'security/email_validation_log_security.xml',
        'security/ir.model.access.csv',
        "views/res_partner_views.xml",
        'views/email_validation_log_views.xml',
    ],
    'installable': True,
    'application': True,
    "license": "LGPL-3"
}
