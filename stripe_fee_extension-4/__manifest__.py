# -*- coding: utf-8 -*-

{
    'name': 'Stripe Fees Extension',
    'version': '1.3',
    'author': 'Craftsync Technologies',
    'maintainer': 'Craftsync Technologies',
    'category': 'Accounting',
    'summary': 'Collect Stripe processing fees from customer.',
    'description': """
Stripe Payment Acquirer Fees Extension: Collect Stripe processing fees from customer.
""",
    'website': 'https://www.craftsync.com',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends': ['payment_stripe'],
    'data': [
        'views/templates.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 49.00,
    'currency': 'EUR'
}
