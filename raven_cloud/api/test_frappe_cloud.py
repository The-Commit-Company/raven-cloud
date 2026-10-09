import time
from types import SimpleNamespace
from unittest.mock import patch

import frappe
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from frappe.tests import IntegrationTestCase

from raven_cloud.api.frappe_cloud import USER_ROLE, exchange_frappe_cloud_token
from raven_cloud.api.notification import check_site_access

ISSUER = "https://central.example.test"
TEAM_USER = "team-0042@frappe-cloud.invalid"


class TestExchangeFrappeCloudToken(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.private_key = Ed25519PrivateKey.generate()
        jwks_client = SimpleNamespace(
            get_signing_key_from_jwt=lambda token: SimpleNamespace(key=self.private_key.public_key())
        )
        for patcher in (
            patch.dict(frappe.conf, {"frappe_cloud_issuer": ISSUER}),
            patch("raven_cloud.api.frappe_cloud.get_jwks_client", return_value=jwks_client),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.site = f"acme-{frappe.generate_hash(length=8)}.example.test"
        frappe.set_user("Guest")

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()
        super().tearDown()

    def mint(self, **claims) -> str:
        payload = {
            "iss": ISSUER,
            "aud": frappe.utils.get_url(),
            "exp": int(time.time()) + 300,
            "sub": "TEAM-0042",
            "team_name": "Acme",
            "scope": "team-identity",
            "hosts": [self.site],
            **claims,
        }
        return jwt.encode(payload, self.private_key, algorithm="EdDSA")

    def exchange(self, site_name: str | None = None, **claims) -> dict:
        return exchange_frappe_cloud_token(self.mint(**claims), site_name or self.site)

    def test_every_site_of_a_team_gets_the_same_keys(self):
        first = self.exchange()
        second = self.exchange("chat.acme.example.test", hosts=[self.site, "chat.acme.example.test"])

        self.assertEqual(first, second)
        self.assertIn("vapid_public_key", first)
        user = frappe.db.get_value("User", {"api_key": first["api_key"]}, ["name", "first_name"], as_dict=True)
        self.assertEqual(user.name, TEAM_USER)
        self.assertEqual(user.first_name, "Acme")
        self.assertIn(USER_ROLE, frappe.get_roles(user.name))

    def test_the_team_owns_the_site_it_registers(self):
        self.exchange()

        self.assertEqual(frappe.db.get_value("RC Site", self.site, "owner"), TEAM_USER)

    def test_a_hostname_the_token_does_not_list_is_refused(self):
        with self.assertRaises(frappe.PermissionError):
            self.exchange("victim.example.test")
        self.assertFalse(frappe.db.exists("RC Site", "victim.example.test"))

    def test_the_team_takes_over_a_hostname_another_account_registered(self):
        frappe.set_user("Administrator")
        frappe.get_doc({"doctype": "RC Site", "site": self.site}).insert()
        site_user = frappe.get_doc({"doctype": "RC Site User", "site": self.site, "user_id": "a@example.test"}).insert()
        frappe.get_doc({"doctype": "RC Site User Token", "user": site_user.name, "fcm_token": "squatter"}).insert()
        frappe.set_user("Guest")

        self.exchange()

        self.assertEqual(frappe.db.get_value("RC Site", self.site, "owner"), TEAM_USER)
        self.assertFalse(frappe.db.exists("RC Site User Token", {"fcm_token": "squatter"}))

    def test_another_account_cannot_use_the_teams_site(self):
        self.exchange()
        other = frappe.get_doc(
            {"doctype": "User", "email": "other@example.test", "first_name": "Other", "roles": [{"role": USER_ROLE}]}
        ).insert(ignore_permissions=True)

        frappe.set_user(other.name)
        with self.assertRaises(frappe.PermissionError):
            check_site_access(self.site)
        frappe.set_user(TEAM_USER)
        check_site_access(self.site)

    def test_a_disabled_team_gets_no_keys(self):
        self.exchange()
        frappe.db.set_value("User", "team-0042@frappe-cloud.invalid", "enabled", 0)

        with self.assertRaises(frappe.AuthenticationError):
            self.exchange()

    def test_a_token_for_another_service_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            self.exchange(aud="https://other.example.test")

    def test_a_token_from_another_issuer_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            self.exchange(iss="https://evil.example.test")

    def test_a_login_token_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            self.exchange(scope="site")

    def test_an_expired_token_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            self.exchange(exp=int(time.time()) - 60)

    def test_a_token_signed_with_another_key_is_refused(self):
        forged = jwt.encode(
            jwt.decode(self.mint(), options={"verify_signature": False}),
            Ed25519PrivateKey.generate(),
            algorithm="EdDSA",
        )

        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(forged, self.site)
