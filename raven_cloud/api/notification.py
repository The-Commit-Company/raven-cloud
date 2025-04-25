import frappe
import firebase_admin
from firebase_admin import messaging
import json
from raven_cloud.utils.fcm import get_app

@frappe.whitelist()
def send(messages):
    """
    API which is a wrapper around the _send function. It takes in the messages and enqueues a background job to send the messages to tokens via FCM.
    Before enqueuing the job, it checks if the user has the necessary permissions to send notifications.
    """

    frappe.only_for(["Raven Cloud User", "System Manager"])

    if isinstance(messages, str):
        messages = json.loads(messages)

    # Enqueue the job of sending notifications
    frappe.enqueue(
        _send,
        messages=messages,
        site_url=frappe.request.host,
        queue="short",
    )

    # TODO: Return the response from api itself.
    return

def _send(messages, site_url: str):
    """
    Send messages to tokens via FCM
        Each message is a dictionary with the following keys:
        - tokens: list[str] - list of device tokens to send the message to
        - notification: dict
            - title: str
            - body: str
        - data: dict - this is for custom data or background messages
        - tag(optional): str - tag to group messages together
        - image(optional): str - image to display in the notification
        - click_action(optional): str - action to perform when the user clicks the notification - web only
    """
    app = get_app()

    # TODO: Check if each message has less than 500 tokens. Else split into multiple messages

    fcm_messages = []
    all_tokens = []

    try:
        for message in messages:
            notification = None
            data = None
            webpush = None
            android = None
            apns = None

            if message.get("notification"):
                notification = messaging.Notification(
                    title=message["notification"]["title"],
                    body=message["notification"]["body"],
                    image=message.get("image", None),
                )

                if message.get("click_action"):
                    if message.get("click_action").startswith("https://"):
                        webpush = messaging.WebpushConfig(
                            fcm_options=messaging.WebpushFCMOptions(
                                link=message.get("click_action", None),
                            ),
                        )
            
                if message.get("tag") or message.get("image"):
                    android = messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            tag=message.get("tag", None),
                            image=message.get("image", None),
                            priority="high",
                        ),
                    )
            
                apns = messaging.APNSConfig(
                    fcm_options=messaging.APNSFCMOptions(
                        image=message.get("image", None),
                    ),
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            content_available=True,
                        ),
                    ),
                )    

            if message.get("data"):
                data = message["data"]

            for token in message.get("tokens", []):

                fcm_message = messaging.Message(
                    token=token,
                    notification=notification,
                    data=data,
                    webpush=webpush,
                    android=android,
                    apns=apns,
                )
                fcm_messages.append(fcm_message)
                all_tokens.append(token)

        # send notifications via fcm in a batch
        response = messaging.send_each(fcm_messages, app=app)

        failed_tokens = []
        success_tokens = []

        # failed and success tokens is used to keep track of the count of failed and success tokens and to store the failed/invalid tokens in RC Invalid Tokens doctype
        if response.failure_count > 0:
            responses = response.responses
            for idx, response in enumerate(responses):
                if response.success:
                    success_tokens.append(all_tokens[idx])
                else:
                    failed_tokens.append(all_tokens[idx])

            # store the failed/invalid tokens in RC Invalid Tokens doctype
            for token in failed_tokens:
                frappe.get_doc({
                    "doctype": "RC Invalid Tokens",
                    "site": site_url,
                    "invalid_token": token,
                }).insert()
        else:
            success_tokens = all_tokens

        # store the response in RC Push Notification Log
        frappe.get_doc({
            "doctype": "RC Push Notification Log",
            "user": frappe.session.user,
            "site": site_url,
            "number_of_messages": len(messages),
            "number_of_tokens": len(all_tokens),
            "success_tokens": len(success_tokens),
            "failed_tokens": len(failed_tokens),
        }).insert()

    except Exception as e:
        frappe.get_doc({
            "doctype": "RC Push Notification Error Log",
            "user": frappe.session.user,
            "site": site_url,
            "error_traceback": frappe.get_traceback(e),
        }).insert()
