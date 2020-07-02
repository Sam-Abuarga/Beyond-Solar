# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Global Search',
    'version': '1.3',
    'category': 'Tools',
    'summary': 'Search any records that you have access by typing a search term',
    'description': """
What is Global search?
======================

Global search lets you search any records that you have access and configured relavent models to. A sales person can search their customers and sales orders, for example, or a project manager could search for project-related tasks.

The feature needs to be enabled by the administrator by installing 'global_search' model and a search box is then available at the top of the menu.

What can I search for?
======================

You can search any records of models for which you have access and related fields which are selected in the configuration menu.

How does it work?
=================

Click the search icon and type a search term into the global box that appears. You can simply click the search button to search aynthing.

You will then see match results in the drop list.

Global Search
Search
Record
Search Record
sales
purchase
product
item
sales order
order
purchase order
project
search fields
fields
user
account
journal
entry
invoice
task
database
quotation
customer
vendor
M2O
M2M
O2M
N-Levels
form view
model
search view
order line
order reference
salesperson
batch record
batches
char
search criteria
advance search
search all record
search specific record
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['web'],
    'data': [
        'security/global_search_security.xml',
        'security/ir.model.access.csv',
        'views/search_config_view.xml',
        'views/global_search_template.xml',
        'wizard/global_search_batch_wizard_view.xml',
        'views/search_config_batch_view.xml'
    ],
    'qweb': [
        'static/src/xml/global_search.xml'
    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    # 'pre_init_hook': 'pre_init_check',
    'license': 'OPL-1',
    'price': 120,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False
}
