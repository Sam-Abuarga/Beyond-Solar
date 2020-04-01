{
    'name': 'Solar Samaritan',
    'category': 'Sales',
    'version': '13.0.1.0.0',
    'author': "Jake Robinson",
    'website': "https://programmedbyjake.com",
    'summary': 'Referral System for Beyond Solar',
    'description': """
    - Allow defining a "referred by" customer on a lead.
    - Send automated emails for  
    """,
    'depends': [
        'base',
        'crm',
        'sale',
    ],
    'data': [
        'assets.xml',
        'security/ir.model.access.csv',

        'data/mail_template.xml',
        'data/base_automation.xml',

        'views/crm_lead.xml',
        'views/sale_referral.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,

    'license': 'OPL-1',
    'support': 'support@programmedbyjake.com',
}
