{
    'name': 'Beyond Solar - Sales',
    'category': 'Sales',
    'version': '13.0.1.0.0',
    'author': "Jake Robinson",
    'website': "https://programmedbyjake.com",
    'summary': 'Sales Order Modifications for Beyond Solar',
    'description': """
    - Custom layout for quotation portal view.
    - Changed quotation portal view "pay now" to "pay deposit", and made a 10% deposit invoice.    
    """,
    'depends': [
        'base',
        'payment',
        'sale',
        'sale_timesheet',
    ],
    'data': [
        'templates/sale_order_portal.xml',

        'views/product_template.xml',
    ],
    'installable': True,
    'application': False,

    'license': 'OPL-1',
    'support': 'support@programmedbyjake.com',
}
