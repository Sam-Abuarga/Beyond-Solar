{
    'name': 'Beyond Solar - Project',
    'category': 'Sales',
    'version': '13.0.1.0.0',
    'author': "Jake Robinson",
    'website': "https://programmedbyjake.com",
    'summary': 'Project Modifications for Beyond Solar',
    'description': """

    """,
    'depends': [
        'base',
        'project',
        'project_enterprise',
        'sale',
        'sale_timesheet',

        'sale_beyond_solar',
    ],
    'data': [
        'assets.xml',

        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'reports/project_task.xml',
        'reports/project_task_swms.xml',

        'templates/project_task.xml',

        'views/connection_diagram.xml',
        'views/project_project.xml',
        'views/project_task.xml',

        'data/mail_template.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,

    'license': 'OPL-1',
    'support': 'support@programmedbyjake.com',
}
