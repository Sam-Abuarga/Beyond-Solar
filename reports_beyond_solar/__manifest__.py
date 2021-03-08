{
    'name': 'Beyond Solar - Reports',
    'category': 'Sales',
    'version': '13.0.1.0.0',
    'author': "Jake Robinson",
    'website': "https://programmedbyjake.com",
    'summary': 'Report Modifications for Beyond Solar',
    'description': """    
    """,
    'depends': [
        'account',
        'sale',
        'project_beyond_solar',
    ],
    'data': [
        'reports/account_move.xml',
        'reports/shared.xml',
        'reports/welcome_pack.xml',

        'views/res_users.xml',
    ],
    'installable': True,
    'application': False,

    'license': 'OPL-1',
    'support': 'support@programmedbyjake.com',
}
