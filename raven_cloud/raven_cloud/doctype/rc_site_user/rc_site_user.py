# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RCSiteUser(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		site: DF.Link
		user_id: DF.Data
	# end: auto-generated types

	pass
