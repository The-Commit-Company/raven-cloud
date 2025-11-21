# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RCPushNotificationLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		failed_tokens: DF.Int
		number_of_messages: DF.Int
		number_of_tokens: DF.Int
		site: DF.Link
		success_tokens: DF.Int
		user: DF.Link
	# end: auto-generated types

	pass


def cleanup_old_logs():
	"""
	Delete RC Push Notification Log entries older than 30 days.
	
	This function runs daily via scheduler. It deletes old logs in batches
	to maintain performance on large tables while avoiding database locks.
	Only logs errors; assumes weekly aggregation has already preserved data.
	"""
	from frappe.utils import add_to_date, getdate, now_datetime
	try:
		# calculate cutoff date - 30 days ago
		cutoff_date = add_to_date(getdate(now_datetime()), days=-30)
		
		batch_size = 5000
		total_deleted = 0
		
		# delete logs older than cutoff date in batches
		while True:
			deleted_count = frappe.db.sql(
				"""
				DELETE FROM `tabRC Push Notification Log`
				WHERE DATE(creation) < %s
				LIMIT %s
				""",
				(cutoff_date, batch_size)
			)
			
			# get affected row count
			rows_deleted = deleted_count if isinstance(deleted_count, int) else 0
			
			if rows_deleted == 0:
				break
			
			total_deleted += rows_deleted
			# commit the changes to ensure data is persisted after each batch
			frappe.db.commit()
			
			# exit if we deleted less than batch size (no more rows to delete)
			if rows_deleted < batch_size:
				break
		
	except Exception:
		frappe.log_error(
			title="Error in cleanup_old_logs",
			message=frappe.get_traceback()
		)