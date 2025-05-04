# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

# import frappe
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
