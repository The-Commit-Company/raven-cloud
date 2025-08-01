# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class RavenMarketplace(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raven_cloud.raven_cloud.doctype.raven_marketplace_linked_app.raven_marketplace_linked_app import RavenMarketplaceLinkedApp

		bot_data: DF.JSON
		description: DF.SmallText
		download_count: DF.Int
		image: DF.AttachImage | None
		is_ai_bot: DF.Check
		linked_apps: DF.Table[RavenMarketplaceLinkedApp]
		long_description: DF.HTMLEditor | None
		marketplace_type: DF.Literal["", "Bot",
                               "Document Notifications", "Schedule Messages"]
		product_name: DF.Data
		status: DF.Literal["Draft", "Published", "In Review", "Attention Required", "Rejected", "Disabled"]
		title: DF.Data
	# end: auto-generated types

	def update_download_count(self, increment: bool = True):
		'''
		Update the download count of the marketplace.
		
		Args:
			increment (bool): If True, increment the count; if False, decrement it.
		'''
		if increment:
			self.db_set('download_count', self.download_count + 1)
		else:
			self.db_set('download_count', self.download_count - 1)


@frappe.whitelist()
def get_marketplace(marketplace_id: str, site_name: str):
	'''
	Fetch the marketplace details for a given marketplace ID and site name.

	Args:
		marketplace_id (str): The ID of the marketplace.
		site_name (str): The name of the site.

	Returns:
		RavenMarketplace: The marketplace document if found, else None.
	
	Steps:
		1. Check if the site_name is registered on RC Site
		2. Check if the marketplace is already downloaded for the site
		3. Fetch the marketplace details
	'''

	if not frappe.db.exists("RC Site", site_name):
		frappe.throw(
			_("Site {0} is not registered on Raven Cloud.").format(site_name))

	if frappe.db.exists("Marketplace Download Logs", {"site_name": site_name, "marketplace_name": marketplace_id, "status": "Success"}):
		frappe.throw(_("Marketplace {0} is already downloaded for site {1}.").format(
			marketplace_id, site_name))

	marketplace = frappe.get_cached_doc("Raven Marketplace", marketplace_id)

	if not marketplace:
		frappe.throw(_("Marketplace {0} not found.").format(marketplace_id))

	return marketplace
