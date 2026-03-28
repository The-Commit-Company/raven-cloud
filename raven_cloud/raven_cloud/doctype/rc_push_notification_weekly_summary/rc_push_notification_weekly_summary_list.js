frappe.listview_settings["RC Push Notification Weekly Summary"] = {
    onload(listview) {
        if (!frappe.user_roles.includes("System Manager")) {
            return;
        }

        listview.page.add_inner_button(__("Run Weekly Aggregation"), () => {
            const dialog = new frappe.ui.Dialog({
                title: __("Run Weekly Aggregation"),
                fields: [
                    {
                        fieldname: "reference_date",
                        fieldtype: "Date",
                        label: __("Any Date In Target Week"),
                        reqd: 1,
                        default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
                        description: __(
                            "This runs the weekly summary aggregation for all sites for the week containing the selected date."
                        ),
                    },
                ],
                primary_action_label: __("Run"),
                primary_action(values) {
                    frappe.call({
                        method: "raven_cloud.doctype.rc_push_notification_weekly_summary.rc_push_notification_weekly_summary.trigger_weekly_aggregation",
                        args: {
                            reference_date: values.reference_date,
                        },
                        freeze: true,
                        freeze_message: __("Aggregating weekly logs for all sites..."),
                        callback: ({ message }) => {
                            if (message) {
                                frappe.msgprint(
                                    __(
                                        "Week {0} to {1}: created {2}, updated {3}, skipped {4}, sites with logs {5}.",
                                        [
                                            message.week_start_date,
                                            message.week_end_date,
                                            message.created,
                                            message.updated,
                                            message.skipped,
                                            message.sites_with_logs,
                                        ]
                                    )
                                );
                            }

                            dialog.hide();
                            listview.refresh();
                        },
                    });
                },
            });

            dialog.show();
        });
    },
};
