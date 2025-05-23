import frappe


def has_app_permission():
	"""Check if user has permission to access the app (for showing the app on app screen)"""
	frappe.only_for("Raven Cloud User")