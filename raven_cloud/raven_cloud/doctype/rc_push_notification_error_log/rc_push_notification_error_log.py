# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RCPushNotificationErrorLog(Document):
	# begin: auto-generated types
	# ruff: noqa

	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		error_response: DF.LongText | None
		error_traceback: DF.LongText | None
		site: DF.Link | None
		user: DF.Link
	# ruff: noqa
	# end: auto-generated types


	pass
