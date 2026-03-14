import frappe
from raven_cloud.raven_cloud.doctype.rc_site_user_token.rc_site_user_token import on_doctype_update

def execute():
    on_doctype_update()
