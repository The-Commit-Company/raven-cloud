import frappe
import firebase_admin
from firebase_admin import messaging
import json
from raven_cloud.utils.fcm import get_app
from urllib.parse import urlparse

@frappe.whitelist()
def send(messages):
    """
    API which is a wrapper around the _send function. It takes in the messages and enqueues a background job to send the messages to tokens via FCM.
    Before enqueuing the job, it checks if the user has the necessary permissions to send notifications.
    """

    def _site_name(site_url: str) -> str:
        return urlparse(site_url).hostname

    user_roles = frappe.get_roles(frappe.session.user)

    if not ("System Manager" in user_roles or "Raven Cloud User" in user_roles):
        frappe.throw("You are not authorized to send notifications", frappe.PermissionError)

    if isinstance(messages, str):
        messages = json.loads(messages)

    site_url = _site_name(frappe.utils.get_url())

    # Enqueue the job of sending notifications
    frappe.enqueue(
        _send,
        messages=messages,
        site_url=site_url,
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
                webpush = messaging.WebpushConfig(
                    fcm_options=messaging.WebpushFcmOptions(
                        link=message["notification"]["click_action"],
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
                "site_url": site_url,
                "invalid_token": token,
            }).insert()
    else:
        success_tokens = all_tokens

    # store the response in RC Push Notification Log
    frappe.get_doc({
        "doctype": "RC Push Notification Log",
        "user": frappe.session.user,
        "number_of_messages": len(messages),
        "number_of_tokens": len(all_tokens),
        "success_tokens": len(success_tokens),
        "failed_tokens": len(failed_tokens),
    }).insert()