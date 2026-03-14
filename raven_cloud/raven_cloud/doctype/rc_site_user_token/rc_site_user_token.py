# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from raven_cloud.utils.rc_caching import clear_push_tokens_for_user_cache


class RCSiteUserToken(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		fcm_token: DF.SmallText
		user: DF.Link
	# end: auto-generated types

	def after_insert(self):
		self.invalidate_cache()

	def after_delete(self):
		self.invalidate_cache()

	def on_update(self):
		self.invalidate_cache()

	def invalidate_cache(self):
		clear_push_tokens_for_user_cache(self.user)


def on_doctype_update():
	"""
	Add unique constraint on user and fcm_token fields
	"""
	frappe.db.add_unique(
		"RC Site User Token",
		fields=["user", "fcm_token"],
		constraint_name="unique_user_fcm_token",
	)
