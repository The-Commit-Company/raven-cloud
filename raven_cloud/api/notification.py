import frappe
import firebase_admin
from firebase_admin import messaging
import json
from raven_cloud.utils.fcm import get_app

@frappe.whitelist()
def send(messages):
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

    if not (frappe.user.has_role("System Manager") or frappe.user.has_role("Raven Cloud User")):
        frappe.throw("You are not authorized to send notifications", frappe.PermissionError)

    if isinstance(messages, str):
        messages = json.loads(messages)

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

    if response.failure_count > 0:
        responses = response.responses
        for idx, response in enumerate(responses):
            if not response.success:
                failed_tokens.append(all_tokens[idx])

    return {
        "success": response.success_count,
        "failure": response.failure_count,
        "failed_tokens": failed_tokens,
    }
