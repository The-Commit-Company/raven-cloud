import json
from typing import Any

import firebase_admin
import frappe
from firebase_admin import messaging
from frappe import _
from frappe.utils import now_datetime
from frappe.utils.response import Response

from raven_cloud.utils.fcm import get_app
from raven_cloud.utils.notification import sanitize_fcm_data, get_background_job_id
from raven_cloud.utils.rc_caching import get_push_tokens_for_user

Message = dict[str, Any]
Messages = list[Message]

@frappe.whitelist(methods=["POST"])
def register_site(site_name: str):
    frappe.only_for('Raven Cloud User')

    # Check if the site is already registered
    if not frappe.db.exists('RC Site', {'site': site_name}):
        frappe.get_doc(
            {
                'doctype': 'RC Site',
                'site': site_name,
            }
        ).insert()

    # update the last registered on and last registered by fields - to keep track of the last time the site was registered and by whom
    frappe.db.set_value(
        'RC Site',
        site_name,
        {
            'last_registered_on': now_datetime(),
            'last_registered_by': frappe.session.user,
        }
    )

    fcm_settings = frappe.get_doc('RC FCM Settings')

    return {
        'config': fcm_settings.firebase_client_configuration,
        'vapid_public_key': fcm_settings.vapid_public_key,
    }


@frappe.whitelist(methods=["POST"])
def send(messages: str, site_name: str):
    """
    API which is a wrapper around the _send function. It takes in the messages and enqueues a background job to send the messages to tokens via FCM.
    Before enqueuing the job, it checks if the user has the necessary permissions to send notifications.
    """

    frappe.only_for('Raven Cloud User')

    # check if the site exists in RC Site
    if not frappe.db.exists('RC Site', site_name):
        frappe.throw(_("Site not created for the user"))

    roles = frappe.get_roles()
    if "System Manager" not in roles or "Administrator" not in roles:
        # check if user has permission to send notifications to this site
        if not frappe.db.exists('RC Site User', {'site': site_name, 'user_id': frappe.session.user}):
            frappe.throw(_("You do not have permission to send notifications to this site."))


    if isinstance(messages, str):
        messages = json.loads(messages)

    job_id = get_background_job_id(messages, site_name)

    # Enqueue the job of sending notifications
    frappe.enqueue(
        _send,
        messages=messages,
        site_url=site_name,
        queue='short',
        job_id=job_id,
        deduplicate=True
    )

    # TODO: Return the response from api itself.
    return


def _send(messages: Messages, site_url: str):
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
            # remove duplicate tokens to avoid sending duplicate notifications
            message_tokens = list(dict.fromkeys(message.get("tokens", [])))

            if not message_tokens:
                continue

            notification = None
            data = None
            webpush = None
            android = None
            apns = None

            if message.get('notification'):
                notification = messaging.Notification(
                    title=message['notification']['title'],
                    body=message['notification']['body'],
                    # image=message.get('image', None),
                )

                if message.get('click_action'):
                    if message.get('click_action').startswith('https://'):
                        webpush = messaging.WebpushConfig(
                            fcm_options=messaging.WebpushFCMOptions(
                                link=message.get('click_action', None),
                            )
                        )
                # temp? don't send image to android for now
                if message.get('tag') or message.get('image'):
                    android = messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            tag=message.get('tag', None),
                            # image=message.get('image', None),
                            priority='high',
                            sound='default',
                        ),
                    )

                apns = messaging.APNSConfig(
                    fcm_options=messaging.APNSFCMOptions(
                        image=message.get('image', None),
                    ),
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            content_available=True,
                            sound='default',
                        ),
                    ),
                )

            if message.get('data'):
                data = sanitize_fcm_data(message['data'])

            for token in message_tokens:
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
                if not frappe.db.exists('RC Invalid Tokens', {'site': site_url, 'invalid_token': token}):
                    frappe.get_doc(
                        {
                            'doctype': 'RC Invalid Tokens',
                            'site': site_url,
                            'invalid_token': token,
                        }
                    ).insert()
        else:
            success_tokens = all_tokens

        # store the response in RC Push Notification Log
        frappe.get_doc(
            {
                'doctype': 'RC Push Notification Log',
                'user': frappe.session.user,
                'site': site_url,
                'number_of_messages': len(messages),
                'number_of_tokens': len(all_tokens),
                'success_tokens': len(success_tokens),
                'failed_tokens': len(failed_tokens),
            }
        ).insert()

    except Exception as e:
        frappe.get_doc(
            {
                'doctype': 'RC Push Notification Error Log',
                'user': frappe.session.user,
                'site': site_url,
                'error_traceback': frappe.get_traceback(e),
                'error_response': json.dumps(messages),
            }
        ).insert()

@frappe.whitelist(methods=["POST"])
def send_to_users(messages: str, site_name: str):
    """
    Send messages to users via FCM.
    Users is a list of user ids (Raven User ids)
    """
    frappe.only_for('Raven Cloud User')

    # check if the site exists
    if not frappe.db.exists('RC Site', site_name):
        frappe.throw(_("Site not registered on Raven Cloud, please ask your System Manager to register the site."))

    roles = frappe.get_roles()
    if "System Manager" not in roles or "Administrator" not in roles:
        # check if user has permission to send notifications to this site
        if not frappe.db.exists('RC Site User', {'site': site_name, 'user_id': frappe.session.user}):
            frappe.throw(_("You do not have permission to send notifications to this site."))

    if isinstance(messages, str):
        messages = json.loads(messages)

    job_id = get_background_job_id(messages, site_name)

    # enqueue the job of sending notifications
    frappe.enqueue(
        _send_to_users,
        messages=messages,
        site_url=site_name,
        queue='short',
        job_id=job_id,
        deduplicate=True
    )

    # TODO: Return the response from api itself.
    return


def _send_to_users(messages: Messages, site_url: str):
    """
    Send messages to users via FCM

    - Messages is a list of messages to send to the users
    Each message is a dictionary with the following keys:
        - users: list(str)
        - notification: dict
            - title: str
            - body: str
        - data: dict - this is for custom data or background messages
        - tag(optional): str - tag to group messages together
        - image(optional): str - image to display in the notification
        - click_action(optional): str - action to perform when the user clicks the notification - web only
    """
    app = get_app()

    fcm_messages = []
    # Track ALL tokens for response processing
    all_tokens = []
    try:
        for message in messages:
            # get tokens for this message only
            message_tokens = []
            for user in message.get("users", []):
                message_tokens.extend(get_push_tokens_for_user(user, site_url))

            # remove duplicate tokens to avoid sending duplicate notifications - not using set() because it doesn't preserve order
            message_tokens = list(dict.fromkeys(message_tokens))

            if not message_tokens:
                continue

            # add this message's tokens to the global list - to keep track of the count of tokens
            all_tokens.extend(message_tokens)

            notification = None
            data = None
            webpush = None
            android = None
            apns = None

            if message.get("notification"):
                notification = messaging.Notification(
                    title=message["notification"]["title"],
                    body=message["notification"]["body"],
                    # image=message.get("image", None),
                )

                if message.get("click_action"):
                    if message.get("click_action").startswith("https://"):
                        webpush = messaging.WebpushConfig(
                            fcm_options=messaging.WebpushFCMOptions(
                                link=message.get("click_action", None),
                            )
                        )

                if message.get("tag") or message.get("image"):
                    android = messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            tag=message.get("tag", None),
                            # image=message.get("image", None),
                            priority="high",
                            sound="default",
                        ),
                    )

                apns = messaging.APNSConfig(
                    fcm_options=messaging.APNSFCMOptions(
                        image=message.get("image", None),
                    ),
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            content_available=True,
                            sound="default",
                        ),
                    ),
                )

            if message.get("data"):
                data = sanitize_fcm_data(message['data'])

            # create FCM messages for THIS message's tokens only
            for token in message_tokens:
                fcm_message = messaging.Message(
                    token=token,
                    notification=notification,
                    data=data,
                    webpush=webpush,
                    android=android,
                    apns=apns,
                )
                fcm_messages.append(fcm_message)

        if not fcm_messages:
            return

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
            "error_response": json.dumps(messages),
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
    user.save(ignore_permissions=True)

    return {
        "api_key": api_key if api_key else user.api_key,
        "api_secret": api_secret,
    }


def check_if_site_exists(site_name: str, throw: bool = True):
    """
    Check if the site exists.
    """
    if not frappe.db.exists("RC Site", site_name):
        if throw:
            frappe.throw(_("Site not registered on Raven Cloud, please ask your System Manager to register the site."))
        else:
            return False
    return True

def get_site_user(site_name: str, user_id: str):
    """
    Get the site user for the given site and user id.
    """
    return frappe.db.exists("RC Site User", {"site": site_name, "user_id": user_id})

@frappe.whitelist(methods=["POST"])
def create_user_token(site_name: str, user_id: str, token: str):
    """
        This api would be used as a sync api between raven cloud and the raven client app.

    """
    # check if the site exists
    check_if_site_exists(site_name)

    site_user = get_site_user(site_name, user_id)

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
        # deduping - add a check to see if the token already exists
        if frappe.db.exists("RC Site User Token", {"user": site_user, "fcm_token": token}):
            return {
                "status": "success",
            }

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
def import_user_tokens(site_name: str, tokens: str):
    """
    Sync user tokens for the given site.
    tokens is a list of dictionaries with the following keys:
        - user: str
        - fcm_token: str
    This API syncs tokens on a per-user basis.
    For each user present in the incoming tokens:
    - Deletes tokens on RC that are not in the incoming set
    - Adds tokens that are not yet on RC
    Tokens for users NOT in the incoming payload are left untouched,
    making this safe to call with partial/chunked token lists.
    """
    check_if_site_exists(site_name)

    try:
        if isinstance(tokens, str):
            tokens = json.loads(tokens)

        # if no tokens are present, return
        if not tokens:
            frappe.db.set_value(
                "RC Site",
                site_name,
                {
                    "last_synced_on": now_datetime(),
                    "last_synced_status": "Success",
                    "last_sync_error": None,
                },
                update_modified=False,
            )
            return {
                "status": "success",
            }

        # building an incoming set for faster lookup
        incoming_users = list({token.get("user") for token in tokens})
        incoming_tokens = {(token.get("user"), token.get("fcm_token")) for token in tokens}

        rc_site_user = frappe.qb.DocType("RC Site User")
        rc_site_user_token = frappe.qb.DocType("RC Site User Token")

        # fetching all the existing tokens on RC for this site
        existing_tokens_query = (
            frappe.qb.from_(rc_site_user_token)
            .inner_join(rc_site_user)
            .on(rc_site_user_token.user == rc_site_user.name)
            .select(rc_site_user_token.fcm_token, rc_site_user_token.name, rc_site_user.user_id)
            .where(rc_site_user.site == site_name)
            .where(rc_site_user.user_id.isin(incoming_users))
        )

        existing_tokens = existing_tokens_query.run(as_dict=True)

        existing_tokens_map = {(row.get("user_id"), row.get("fcm_token")) for row in existing_tokens}

        # deleting tokens on server that are not in incoming tokens
        tokens_to_delete = [
            row["name"] for row in existing_tokens
            if (row["user_id"], row["fcm_token"]) not in incoming_tokens
        ]

        # deleting the tokens on RC that are not present in the incoming tokens
        for token_name in tokens_to_delete:
            frappe.delete_doc("RC Site User Token", token_name)

        # adding tokens that don't exist on server
        tokens_to_add = [
            token for token in tokens
            if (token.get("user"), token.get("fcm_token")) not in existing_tokens_map
        ]


        user_map = {}

        for token in tokens_to_add:
            user_id = token.get("user")
            fcm_token = token.get("fcm_token")

            if user_id not in user_map:
                user = get_site_user(site_name, user_id)
                if not user:
                    user = frappe.get_doc({
                        "doctype": "RC Site User",
                        "site": site_name,
                        "user_id": user_id,
                    }).insert().name

                user_map[user_id] = user

            frappe.get_doc({
                "doctype": "RC Site User Token",
                "user": user_map[user_id],
                "fcm_token": fcm_token,
            }).insert()

        frappe.db.set_value(
            "RC Site",
            site_name,
            {
                "last_synced_on": now_datetime(),
                "last_synced_status": "Success",
                "last_sync_error": None,
                "last_synced_by": frappe.session.user,
            },
            update_modified=False,
        )
    except Exception as e:
        frappe.db.set_value(
            "RC Site",
            site_name,
            {
                "last_synced_status": "Failed",
                "last_sync_error": str(e),
                "last_synced_by": frappe.session.user,
            },
            update_modified=False,
        )
        frappe.log_error(title=f"Error syncing user tokens for {site_name}", message=frappe.get_traceback())
        frappe.throw(_(f"Error syncing user tokens for {site_name} - {str(e)}"))

    return {
        "status": "success",
    }

@frappe.whitelist(methods=["POST"])
def delete_user_token(site_name: str, user_id: str, token: str):
    """
    Delete a user token for the given site and user.
    """
    check_if_site_exists(site_name)

    site_user = get_site_user(site_name, user_id)

    id = frappe.db.exists("RC Site User Token", {"user": site_user, "fcm_token": token})

    if not id:
        return

    doc = frappe.get_doc("RC Site User Token", id)
    doc.delete()


@frappe.whitelist(methods=["POST"])
def create_site_channel(channel_id: str, site_name: str):
    """
    API for channel/topic creation.
    This would ideally be called when the user creates a new channel/topic in the raven client app.
    """

    site = frappe.db.exists("RC Site", site_name)

    if not site:
        frappe.throw(_("Site not registered on Raven Cloud, please ask your System Manager to register the site."))

    try:

        # create a new channel if it doesn't exist
        if not frappe.db.exists("RC Site Channel", {"site": site, "channel_id": channel_id}):
            frappe.get_doc({
                "doctype": "RC Site Channel",
                "site": site,
                "channel_id": channel_id,
            }).insert()

    except Exception as e:
        frappe.log_error(title=f"Error creating site channel for {channel_id} of {site_name}", message=frappe.get_traceback())
        frappe.throw(_(f"Error creating site channel for {channel_id} of {site_name} - {str(e)}"))

    return {
        "status": "success",
    }

# @frappe.whitelist(methods=["POST"])
def subscribe_to_site_channel(channel_id: str, user_id: str, site_name: str):
    """
    API for channel/topic based subscription.

    Create a RC Site Channel if site channel does not exist.
    Create a RC Site User if site user does not exist.
    Create a RC Site Channel subscription if the user is not subscribed to the channel.
    """

    site = frappe.db.exists("RC Site", site_name)

    if not site:
        frappe.throw(_("Site not registered on Raven Cloud, please ask your System Manager to register the site."))

    try:
        channel = frappe.db.exists("RC Site Channel", {"site": site, "channel_id": channel_id})

        if not channel:
            channel = frappe.get_doc({
                "doctype": "RC Site Channel",
                "site": site,
                "channel_id": channel_id,
            }).insert()

        # check if the user exists
        user = frappe.db.exists("RC Site User", {"site": site, "user_id": user_id})

        if not user:
            user = frappe.get_doc({
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

    except Exception as e:
        frappe.log_error(title=f"Error subscribing to site channel for {user_id} of {site_name}", message=frappe.get_traceback())
        frappe.throw(_(f"Error subscribing to site channel for {user_id} of {site_name} - {str(e)}"))

    return {
        "status": "success",
    }

# @frappe.whitelist(methods=["POST"])
def unsubscribe_from_site_channel(channel_id: str, user_id: str, site_name: str):
    """
    API for channel/topic based unsubscription.

    Delete a RC Site Channel subscription if the user is subscribed to the channel.
    """

    site = frappe.db.exists("RC Site", site_name)

    if not site:
        frappe.throw(_("Site not registered on Raven Cloud, please ask your System Manager to register the site."))

    # channel subscription only exists if the channel and user exists, so we don't need to check for the existence of the channel and user
    channel = frappe.db.get_value("RC Site Channel", {"site": site, "channel_id": channel_id}, ["name"])
    user = frappe.db.get_value("RC Site User", {"site": site, "user_id": user_id}, ["name"])

    frappe.db.delete("RC Site Channel Subscription", {"user": user, "channel": channel})

    return {
        "status": "success",
    }

# @frappe.whitelist(methods=["POST"])
def bulk_create_site_user_and_token(site_name: str, users: list[dict]):
    """
    Bulk create site user and token for the given site and users.

    users is a list of dictionaries with the following keys:
        - user_id: str
        - token: str
    """

    error_messages = []

    for user in users:
        try:
            create_site_user_and_token(site_name, user.get("user_id"), user.get("token"))
        except Exception as e:
            error_message = f"Error creating site user and token for {user.get('user_id')} of {site_name}"
            error_messages.append(f"{error_message} - {str(e)}")
            frappe.log_error(title=error_message, message=frappe.get_traceback())

    if error_messages:
        frappe.throw(_(f"Failed to create some site users and tokens: {'; '.join(error_messages)}"))

    return {
        "status": "success",
    }

@frappe.whitelist(methods=["POST"])
def sync_invalid_tokens(site_name: str, batch_size: int = 10):
    """
    Sync Invalid Tokens is called by the client site(raven client) by sending in site name and batch size.
    We then fetch the invalid tokens from the RC Invalid tokens and send it to the client site.
    Meanwhile we delete the invalid tokens from the RC Invalid tokens.

    The client site will then delete the invalid tokens from the local database and send the token ids to the server.
    We then delete the invalid tokens from the RC Invalid tokens.
    This is done in batches. We send has_more flag to client site to let them know that there are more invalid tokens to be deleted.
    Until has_more is True, the client site will keep calling this API.

    This is a way to ensure that the invalid tokens are deleted from the RC Invalid tokens and the client site.

    """
    frappe.only_for("Raven Cloud User")
    check_if_site_exists(site_name, throw=True)

    # Get count first to determine has_more
    total_count = frappe.db.count("RC Invalid Tokens", filters={"site": site_name})

    # If there are no invalid tokens, we return an empty list with has_more as False.
    if not total_count:
        return {
            "invalid_tokens": [],
            "has_more": False,
            "processed_count": 0,
            "total_remaining": 0
        }

    # Fetch the batch of invalid tokens
    invalid_tokens = frappe.db.get_list(
        "RC Invalid Tokens",
        filters={"site": site_name},
        fields=["invalid_token", "name"],
        order_by="creation asc",
        start=0,
        page_length=batch_size,
    )

    if not invalid_tokens:
        return {
            "invalid_tokens": [],
            "has_more": False,
            "processed_count": 0,
            "total_remaining": 0
        }

    token_ids = [token.get("name") for token in invalid_tokens]

    try:
        # Delete the invalid tokens from the RC Invalid tokens
        frappe.db.delete("RC Invalid Tokens", {"name": ("in", token_ids)})

        # Calculate the remaining count and has_more flag
        remaining_count = total_count - len(invalid_tokens)
        has_more = remaining_count > 0

        return {
            "invalid_tokens": invalid_tokens,
            "has_more": has_more,
            "processed_count": len(invalid_tokens),
            "total_remaining": remaining_count
        }

    except Exception as e:
        frappe.log_error(
            title=f"Error in sync_invalid_tokens for {site_name}",
            message=frappe.get_traceback()
        )
        frappe.throw(_(f"Failed to sync invalid tokens: {str(e)}"))
