from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

import raven_cloud.api.notification as notification_api


class TestNotificationSendToUsers(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.site_name = f"rc-push-repro-{frappe.generate_hash(length=8)}.test"
        frappe.get_doc({"doctype": "RC Site", "site": self.site_name}).insert(ignore_permissions=True)

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()

    def create_site_user_with_token(self, user_id: str, token: str):
        site_user = frappe.get_doc(
            {"doctype": "RC Site User", "site": self.site_name, "user_id": user_id}
        ).insert(ignore_permissions=True)
        frappe.get_doc(
            {"doctype": "RC Site User Token", "user": site_user.name, "fcm_token": token}
        ).insert(ignore_permissions=True)

    def test_send_to_users_should_send_once_for_duplicate_users(self):
        self.create_site_user_with_token("prathamesh@example.com", "tok-prathamesh")

        sent_tokens = []

        with patch.object(notification_api, "get_app", return_value=object()), patch.object(
            notification_api.messaging,
            "Message",
            side_effect=lambda **kwargs: SimpleNamespace(token=kwargs["token"]),
        ), patch.object(
            notification_api.messaging,
            "send_each",
            side_effect=lambda fcm_messages, app=None: (
                sent_tokens.extend(message.token for message in fcm_messages)
                or SimpleNamespace(failure_count=0, responses=[])
            ),
        ):
            notification_api._send_to_users(
                [{"users": ["prathamesh@example.com", "prathamesh@example.com", "prathamesh@example.com"]}],
                self.site_name,
            )

        log = frappe.get_last_doc("RC Push Notification Log", filters={"site": self.site_name})

        self.assertEqual(["tok-prathamesh"], sent_tokens)
        self.assertEqual(1, log.number_of_tokens)

    def test_send_to_users_should_send_once_for_shared_token(self):
        self.create_site_user_with_token("prathamesh@example.com", "tok-shared")
        self.create_site_user_with_token("aditya@example.com", "tok-shared")

        sent_tokens = []

        with patch.object(notification_api, "get_app", return_value=object()), patch.object(
            notification_api.messaging,
            "Message",
            side_effect=lambda **kwargs: SimpleNamespace(token=kwargs["token"]),
        ), patch.object(
            notification_api.messaging,
            "send_each",
            side_effect=lambda fcm_messages, app=None: (
                sent_tokens.extend(message.token for message in fcm_messages)
                or SimpleNamespace(failure_count=0, responses=[])
            ),
        ):
            notification_api._send_to_users(
                [{"users": ["prathamesh@example.com", "aditya@example.com"]}],
                self.site_name,
            )

        log = frappe.get_last_doc("RC Push Notification Log", filters={"site": self.site_name})

        self.assertEqual(["tok-shared"], sent_tokens)
        self.assertEqual(1, log.number_of_tokens)
