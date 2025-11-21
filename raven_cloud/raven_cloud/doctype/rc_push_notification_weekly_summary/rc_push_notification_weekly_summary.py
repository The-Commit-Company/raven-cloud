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


def aggregate_weekly_logs():
	"""
	Aggregate RC Push Notification Log entries for the previous week.
	
	This function is designed to run weekly (on Sunday) via scheduler.
	It processes all logs from the previous week, groups them by site,
	and creates summary records with aggregated statistics.
	"""
	# Calculate previous week's date range
	today = getdate(now_datetime())
	last_week = add_to_date(today, days=-7)
	week_start = getdate(get_first_day_of_week(last_week))
	week_end = getdate(get_last_day_of_week(last_week))

	# Aggregate logs by site for the previous week using efficient SQL
	results = frappe.db.sql(
		"""
		SELECT 
			site,
			COUNT(*) as logs_processed,
			SUM(number_of_messages) as total_messages,
			SUM(number_of_tokens) as total_tokens,
			SUM(COALESCE(success_tokens, 0)) as total_success_tokens,
			SUM(COALESCE(failed_tokens, 0)) as total_failed_tokens
		FROM `tabRC Push Notification Log`
		WHERE DATE(creation) >= %s AND DATE(creation) <= %s
		GROUP BY site
		""",
		(week_start, week_end),
		as_dict=True,
	)

	# Create weekly summary records for each site
	for result in results:
		try:
			# Check if a summary already exists for this site and week
			existing = frappe.db.exists(
				"RC Push Notification Weekly Summary",
				{"site": result.site, "week_start_date": week_start},
			)

			if existing:
				# Update existing summary record
				doc = frappe.get_doc("RC Push Notification Weekly Summary", existing)
				doc.total_messages = result.total_messages or 0
				doc.total_tokens = result.total_tokens or 0
				doc.total_success_tokens = result.total_success_tokens or 0
				doc.total_failed_tokens = result.total_failed_tokens or 0
				doc.logs_processed = result.logs_processed or 0
				doc.aggregated_on = now_datetime()
				doc.save()
			else:
				# Create new summary record
				doc = frappe.get_doc(
					{
						"doctype": "RC Push Notification Weekly Summary",
						"site": result.site,
						"week_start_date": week_start,
						"week_end_date": week_end,
						"total_messages": result.total_messages or 0,
						"total_tokens": result.total_tokens or 0,
						"total_success_tokens": result.total_success_tokens or 0,
						"total_failed_tokens": result.total_failed_tokens or 0,
						"logs_processed": result.logs_processed or 0,
						"aggregated_on": now_datetime(),
					}
				)
				doc.save()
		except Exception:
			frappe.log_error(
				title=f"Error creating/updating weekly summary for site {result.site} for week {week_start} to {week_end}",
				message=frappe.get_traceback()
			)