import frappe


def execute():
	"""
	Patch to cleanup old RC Push Notification Log entries.

    This patch deletes RC Push Notification Log entries older than 30 days
	"""
	from frappe.utils import add_to_date, getdate
	
	try:
		# Calculate cutoff date - 30 days ago
		cutoff_date = add_to_date(getdate(), days=-30)
		
		frappe.db.sql(
			"""
			DELETE log 
			FROM `tabRC Push Notification Log` log
			INNER JOIN `tabRC Push Notification Weekly Summary` summary
				ON summary.site = log.site
				AND DATE(log.creation) BETWEEN summary.week_start_date AND summary.week_end_date
			WHERE DATE(log.creation) < %s
		""", (cutoff_date)
		)

	except Exception:
		frappe.log_error(
			title="Error in cleanup_old_notification_logs patch",
			message=frappe.get_traceback(),
		)