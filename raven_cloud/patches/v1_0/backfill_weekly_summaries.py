
import frappe
from frappe.utils import (
	getdate,
	now_datetime,
)


def execute():
    """
    Patch to backfill weekly summaries for existing RC Push Notification Log entries.

    This patch aggregates all historical logs into weekly summaries by site.
    Backfill weekly summaries for all existing notification logs.

    Strategy:
    1. Run an efficient SQL query that groups ALL logs by (site, week)
    2. Process results and create summary records
    """ 

    results = frappe.db.sql(
        """
        SELECT 
            site,
            DATE(DATE_SUB(creation, INTERVAL WEEKDAY(creation) DAY)) as week_start_date,
            DATE(DATE_ADD(DATE_SUB(creation, INTERVAL WEEKDAY(creation) DAY), INTERVAL 6 DAY)) as week_end_date,
            COUNT(*) as logs_processed,
            SUM(number_of_messages) as total_messages,
            SUM(number_of_tokens) as total_tokens,
            SUM(COALESCE(success_tokens, 0)) as total_success_tokens,
            SUM(COALESCE(failed_tokens, 0)) as total_failed_tokens
        FROM `tabRC Push Notification Log`
        GROUP BY site, week_start_date
        ORDER BY week_start_date, site
        """,
        as_dict=True,
    )

    if not results:
        print("No logs found to aggregate. Skipping backfill.")
        return

    print(f"Processing {len(results)} site-week combinations...")

    for result in results:
        existing = frappe.db.exists(
            "RC Push Notification Weekly Summary",
            {"site": result.site, "week_start_date": result.week_start_date}
        )

        # if site not found in RC Site, skip
        if not frappe.db.exists("RC Site", {"name": result.site}):
            continue

        if not existing:
            doc = frappe.get_doc({
				"doctype": "RC Push Notification Weekly Summary",
				"site": result.site,
				"week_start_date": getdate(result.week_start_date),
				"week_end_date": getdate(result.week_end_date),
				"total_messages": result.total_messages or 0,
				"total_tokens": result.total_tokens or 0,
				"total_success_tokens": result.total_success_tokens or 0,
				"total_failed_tokens": result.total_failed_tokens or 0,
				"logs_processed": result.logs_processed or 0,
				"aggregated_on": now_datetime(),
			})
            doc.save()

    print("Backfill completed for {len(results)} site-week combinations")