# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
	add_to_date,
	get_first_day_of_week,
	get_last_day_of_week,
	getdate,
	now_datetime,
)


class RCPushNotificationWeeklySummary(Document):
	# begin: auto-generated types
	# ruff: noqa

	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		aggregated_on: DF.Datetime | None
		logs_processed: DF.Int
		site: DF.Link | None
		total_failed_tokens: DF.Int
		total_messages: DF.Int
		total_success_tokens: DF.Int
		total_tokens: DF.Int
		week_end_date: DF.Date | None
		week_start_date: DF.Date | None
	# ruff: noqa
	# end: auto-generated types
	pass

