// Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
// For license information, please see license.txt

frappe.ui.form.on("RC FCM Settings", {
    refresh(frm) {

        frm.add_custom_button(_("Send Test Notification"), () => {

            let d = new frappe.ui.Dialog({
                title: "Send Test Notification",
                fields: [
                    {
                        fieldname: "title",
                        label: "Title",
                        fieldtype: "Data",
                        reqd: 1,
                        default: "Adam in #general",
                    },
                    {
                        fieldname: "body",
                        label: "Body",
                        fieldtype: "Text",
                        reqd: 1,
                        default: "Hey this is a test notification",
                    },
                    {
                        fieldname: "image",
                        label: "Image",
                        fieldtype: "Data",
                    },
                    {
                        fieldname: "token",
                        label: "Token",
                        fieldtype: "Data",
                        reqd: 1,
                        length: 400
                    }
                ],
                primary_action_label: "Send",
                primary_action: () => {
                    let data = d.get_values();

                    frappe.call('raven_cloud.api.notification.send', {
                        messages: [
                            {
                                tokens: [data.token],
                                notification: {
                                    title: data.title,
                                    body: data.body,
                                    image: data.image,
                                },
                                data: {
                                    title: data.title,
                                    body: data.body,
                                    image: data.image,
                                    token: data.token,
                                    channel_id: "general",
                                    site_name: "raven-dev.frappe.cloud",
                                }
                            }
                        ]
                    }).then((r) => {
                        if (r.message) {
                            let message = `Notification sent successfully to ${r.message.success} tokens`;
                            if (r.message.failure > 0) {
                                message += ` and failed to send to ${r.message.failure} tokens.`;
                            }
                            frappe.msgprint(message);
                        }

                        d.hide();
                    })
                }
            })
            d.show();

        });
    },
});
