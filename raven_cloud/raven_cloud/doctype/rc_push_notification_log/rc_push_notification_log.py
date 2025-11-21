# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, getdate


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
    Delete RC Push Notification Log entries older than 30 days and for which summary is created already.

    This function runs daily via scheduler.
    """

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
		""",
            (cutoff_date),
        )

    except Exception:
        frappe.log_error(
            title="Error in cleanup_old_logs", message=frappe.get_traceback()
        )