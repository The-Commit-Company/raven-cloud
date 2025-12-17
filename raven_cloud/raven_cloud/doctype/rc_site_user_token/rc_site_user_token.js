// Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
// For license information, please see license.txt

frappe.ui.form.on("RC Site User Token", {
    refresh(frm) {

        // a button which triggers a simulation of sending a test notification to the user
        frm.add_custom_button("Send Test Notification", () => {

            // get the site name from the user, ask the user for the site name

            let site_name;

            let d = new frappe.ui.Dialog({
                title: "Send Test Notification",
                fields: [
                    {
                        fieldname: "site_name",
                        label: "Site Name",
                        fieldtype: "Data",
                    }
                ],
                primary_action_label: "Send",
                primary_action(values) {
                    console.log(values);
                    site_name = values.site_name;

                    frappe.call("raven_cloud.api.notification.send", {
                        messages: [
                            {
                                tokens: [frm.doc.fcm_token],
                                notification: {
                                    title: "Test Notification",
                                    body: "This is a test notification",
                                },
                            }
                        ],
                        site_name: values.site_name,
                    }).then((r) => {
                        frappe.msgprint(`Test notification sending attempt completed.`);

                        d.hide();
                    });
                }
            });

            d.show();

        });

    },
});
