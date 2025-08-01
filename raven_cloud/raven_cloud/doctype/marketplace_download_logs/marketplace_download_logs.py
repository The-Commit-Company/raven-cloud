# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class MarketplaceDownloadLogs(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		downloaded_at: DF.Datetime
		marketplace_name: DF.Link
		marketplace_type: DF.Data
		product_name: DF.Data
		requested_by_user: DF.Data
		requested_by_user_name: DF.Data | None
		site_name: DF.Link
		status: DF.Literal["", "Pending", "Success", "Failed"]
		timezone: DF.Data
		user: DF.Link
	# end: auto-generated types
	
	def before_insert(self):
		'''
			set the current user as the user who requested the download
		'''
		self.user = frappe.session.user

		# check if for site_name already exists
		if frappe.db.exists("Marketplace Download Logs", {"site_name": self.site_name, "marketplace_name": self.marketplace_name, "status": "Success"}):
			frappe.throw(_("Marketplace Already downloaded for this site."))

	def on_update(self):
		'''
			increase the download count of the marketplace
		'''
		old_doc = self.get_doc_before_save()
		
		if old_doc and old_doc.status != "Success" and self.status == "Success":
			# If the status changed to Success, increment the download count
			marketplace = frappe.get_doc("Raven Marketplace", self.marketplace_name)
			marketplace.update_download_count(increment=True)
