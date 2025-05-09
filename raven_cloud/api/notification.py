import frappe
from frappe.utils.response import Response
import firebase_admin
from firebase_admin import messaging
import json
from raven_cloud.utils.fcm import get_app
from raven_cloud.utils.rc_caching import get_push_tokens_for_user

@frappe.whitelist()
def register_site(site_name: str):
    frappe.only_for("Raven Cloud User")

    # Check if the site is already registered
    if not frappe.db.exists("RC Site", {"site": site_name}):
        frappe.get_doc({
            "doctype": "RC Site",
            "site": site_name,
        }).insert()

    fcm_settings = frappe.get_doc("RC FCM Settings")

    return {
		"config": fcm_settings.firebase_client_configuration,
		"vapid_public_key": fcm_settings.vapid_public_key,
	}

@frappe.whitelist()
def send(messages, site_name: str):
    """
    API which is a wrapper around the _send function. It takes in the messages and enqueues a background job to send the messages to tokens via FCM.
    Before enqueuing the job, it checks if the user has the necessary permissions to send notifications.
    """

    frappe.only_for("Raven Cloud User")

    # check if the site exists in RC Site
    if not frappe.db.exists("RC Site", site_name):
        frappe.throw("Site not created for the user")

    if isinstance(messages, str):
        messages = json.loads(messages)

    # Enqueue the job of sending notifications
    frappe.enqueue(
        _send,
        messages=messages,
        site_url=site_name,
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
                # check if the token is already in the RC Invalid Tokens doctype for the same site - if not then insert it
                if not frappe.db.exists("RC Invalid Tokens", {"site": site_url, "invalid_token": token}):
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

def _send_to_tokens(messages, site_url: str, users: list[str]):
    """
    Send messages to users via FCM
    
    - Users is a list of user ids (Raven User ids)
    - Messages is a list of messages to send to the users
    Each message is a dictionary with the following keys:
        - notification: dict
            - title: str
            - body: str
        - data: dict - this is for custom data or background messages
        - tag(optional): str - tag to group messages together
        - image(optional): str - image to display in the notification
        - click_action(optional): str - action to perform when the user clicks the notification - web only
    """
    app = get_app()

    # get the push tokens for the users
    all_tokens = []
    for user in users:
        all_tokens.extend(get_push_tokens_for_user(user))

    fcm_messages = []
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

            for token in all_tokens:
                fcm_message = messaging.Message(
                    token=token,
                    notification=notification,
                    data=data,
                    webpush=webpush,
                    android=android,
                    apns=apns,
                )
                fcm_messages.append(fcm_message)

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
                # check if the token is already in the RC Invalid Tokens doctype for the same site - if not then insert it
                if not frappe.db.exists("RC Invalid Tokens", {"site": site_url, "invalid_token": token}):
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

@frappe.whitelist(methods=["POST"])
def generate_api_keys():
    """
    Generate api key and api secret for the session user, stores it in User doctype and returns the api key and api secret
    """
    frappe.only_for(["Raven Cloud User", "System Manager"])


    # storing api key and secret in a separate variable(to return) as upon saving the secret it will be a password field.
    user = frappe.get_doc("User", frappe.session.user)
    api_secret = frappe.generate_hash(length=15)
    api_key = None
    if not user.api_key:
        api_key = frappe.generate_hash(length=15)
        user.api_key = api_key
    user.api_secret = api_secret
    user.save()

    return {
        "api_key": api_key if api_key else user.api_key,
        "api_secret": api_secret,
    }

@frappe.whitelist(methods=["POST"])
def create_site_user_and_token(site_name: str, user_id: str, token: str):
    """
        This api would be used as a sync api between raven cloud and the raven client app.
        
    """
    # check if the site exists
    if not frappe.db.exists("RC Site", site_name):
        frappe.throw("Site not registered on Raven Cloud, please ask your System Manager to register the site.")

    site_user = frappe.db.exists("RC Site User", {"site": site_name, "user_id": user_id})

    # check if the site user already exists, if not then create a new site user
    if not site_user:

        site_user = frappe.get_doc({
            "doctype": "RC Site User",
            "site": site_name,
            "user_id": user_id,
        })
        site_user.insert()

        # store the token in the RC Site User doctype
        frappe.get_doc({
            "doctype": "RC Site User Token",
            "user": site_user.name,
            "fcm_token": token,
        }).insert()

    else:
        # store the token in the RC Site User doctype
        frappe.get_doc({
            "doctype": "RC Site User Token",
            "user": site_user,
            "fcm_token": token,
        }).insert()

    return {
        "status": "success",
    }

@frappe.whitelist(methods=["POST"])
def create_site_channel(channel_id: str, site_name: str):
    """
    API for channel/topic creation.
    This would ideally be called when the user creates a new channel/topic in the raven client app.
    """

    site = frappe.db.exists("RC Site", site_name)

    if not site:
        frappe.throw("Site not registered on Raven Cloud, please ask your System Manager to register the site.")

    # create a new channel if it doesn't exist
    if not frappe.db.exists("RC Site Channel", {"site": site, "channel_id": channel_id}):
        frappe.get_doc({
            "doctype": "RC Site Channel",
            "site": site,
            "channel_id": channel_id,
        }).insert()
    
    return {
        "status": "success",
    }

@frappe.whitelist(methods=["POST"])
def subscribe_to_site_channel(channel_id: str, user_id: str, site_name: str):
    """
    API for channel/topic based subscription.

    Create a RC Site Channel if site channel does not exist.
    Create a RC Site User if site user does not exist.
    Create a RC Site Channel subscription if the user is not subscribed to the channel.
    """

    site = frappe.db.exists("RC Site", site_name)

    if not site:
        frappe.throw("Site not registered on Raven Cloud, please ask your System Manager to register the site.")
    
    channel = frappe.db.exists("RC Site Channel", {"site": site, "channel_id": channel_id})

    if not channel:
        frappe.get_doc({
            "doctype": "RC Site Channel",
            "site": site,
            "channel_id": channel_id,
        }).insert()
    
    # check if the user exists
    user = frappe.db.exists("RC Site User", {"site": site, "user_id": user_id})

    if not user:
        frappe.get_doc({
            "doctype": "RC Site User",
            "site": site,
            "user_id": user_id,
        }).insert()

    # check if the user is subscribed to the channel
    if not frappe.db.exists("RC Site Channel Subscription", {"user": user, "channel": channel}):
        frappe.get_doc({
            "doctype": "RC Site Channel Subscription",
            "user": user,
            "channel": channel,
        }).insert()

    return {
        "status": "success",
    }

@frappe.whitelist(methods=["POST"])
def unsubscribe_from_site_channel(channel_id: str, user_id: str, site_name: str):
    """
    API for channel/topic based unsubscription.

    Delete a RC Site Channel subscription if the user is subscribed to the channel.
    """

    site = frappe.db.exists("RC Site", site_name)

    if not site:
        frappe.throw("Site not registered on Raven Cloud, please ask your System Manager to register the site.")
    
    # channel subscription only exists if the channel and user exists, so we don't need to check for the existence of the channel and user
    channel = frappe.db.get_value("RC Site Channel", {"site": site, "channel_id": channel_id}, ["name"])
    user = frappe.db.get_value("RC Site User", {"site": site, "user_id": user_id}, ["name"])

    frappe.db.delete("RC Site Channel Subscription", {"user": user, "channel": channel})

    return {
        "status": "success",
    }
