# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RCSite(Document):
	# begin: auto-generated types
	# ruff: noqa

	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		last_registered_by: DF.Link | None
		last_registered_on: DF.Datetime | None
		last_sync_error: DF.SmallText | None
		last_synced_by: DF.Link | None
		last_synced_on: DF.Datetime | None
		last_synced_status: DF.Literal["", "Failed", "Success"]
		site: DF.Data
	# ruff: noqa
	# end: auto-generated types


	pass
