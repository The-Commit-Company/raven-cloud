# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RCInvalidTokens(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        invalid_token: DF.Text
        site: DF.Link
    # end: auto-generated types

    def after_insert(self):
        self.invalidate_cache_for_user()

    def on_trash(self):
        self.invalidate_cache_for_user()

    def invalidate_cache_for_user(self):
        from raven_cloud.utils.rc_caching import clear_push_tokens_for_user_cache

        rc_site_user_token = frappe.qb.DocType("RC Site User Token")
        rc_site_user = frappe.qb.DocType("RC Site User")

        # get the user ids of the users who have the invalid token for the site
        users = (
            frappe.qb.from_(rc_site_user_token)
            .inner_join(rc_site_user)
            .on(rc_site_user_token.user == rc_site_user.name)
            .select(rc_site_user_token.user)
            .where(rc_site_user_token.fcm_token == self.invalid_token)
            .where(rc_site_user.site == self.site)
            .distinct()
            .run(pluck=True)
        )

        # invalidate the cache for the users
        for site_user_id in users:
            clear_push_tokens_for_user_cache(site_user_id)