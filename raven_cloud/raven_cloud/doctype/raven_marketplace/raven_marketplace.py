# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RavenMarketplace(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raven_cloud.raven_cloud.doctype.raven_marketplace_linked_app.raven_marketplace_linked_app import RavenMarketplaceLinkedApp

		description: DF.SmallText
		image: DF.AttachImage | None
		is_ai_bot: DF.Check
		linked_apps: DF.Table[RavenMarketplaceLinkedApp]
		long_description: DF.TextEditor | None
		raven_bot: DF.Link
		status: DF.Literal["Draft", "Published", "In Review", "Attention Required", "Rejected", "Disabled"]
		title: DF.Data
	# end: auto-generated types
	pass
