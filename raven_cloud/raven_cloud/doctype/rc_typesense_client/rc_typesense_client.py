# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from raven_cloud.api.typesense import get_typesense_client, get_collection_schema


class RCTypesenseClient(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        api_key: DF.Data | None
        hash: DF.Data | None
        key_id: DF.Data | None
        site: DF.Link
    # end: auto-generated types

    def before_insert(self):
        self.hash = frappe.generate_hash(length=10)

        client = get_typesense_client()
        key = client.keys.create({
            "description": f"API key for {self.site}",
            "actions": ["*"],
            "collections": [f"{self.hash}_messages"],
            "autodelete": True,
        })
        self.api_key = key["value"]
        self.key_id = key["id"]

        client.collections.create(get_collection_schema(self.hash))
