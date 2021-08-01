{
    'name': 'Brighte Green Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: Brighte Green',
    'version': '13.0.0',
    'description': "Pay Using Brighte Green",
    'depends': [
        'payment',
        'sale',
    ],
    'data': [
        'templates/payment_transfer.xml',
        'templates/sale_order_portal.xml',

        'views/payment_acquirer.xml',
        'views/sale_order.xml',

        'data/mail_activity_type.xml',
        'data/payment_acquirer.xml',
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
