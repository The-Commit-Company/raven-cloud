import time
from types import SimpleNamespace
from unittest.mock import patch

import frappe
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from frappe.tests import IntegrationTestCase

from raven_cloud.api.frappe_cloud import USER_ROLE, exchange_frappe_cloud_token

ISSUER = "https://central.example.test"


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
            **claims,
        }
        return jwt.encode(payload, self.private_key, algorithm="EdDSA")

    def test_every_site_of_a_team_gets_the_same_keys(self):
        first = exchange_frappe_cloud_token(self.mint())
        second = exchange_frappe_cloud_token(self.mint())

        self.assertEqual(first, second)
        user = frappe.db.get_value("User", {"api_key": first["api_key"]}, ["name", "first_name"], as_dict=True)
        self.assertEqual(user.name, "team-0042@frappe-cloud.invalid")
        self.assertEqual(user.first_name, "Acme")
        self.assertIn(USER_ROLE, frappe.get_roles(user.name))

    def test_a_disabled_team_gets_no_keys(self):
        exchange_frappe_cloud_token(self.mint())
        frappe.db.set_value("User", "team-0042@frappe-cloud.invalid", "enabled", 0)

        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(self.mint())

    def test_a_token_for_another_service_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(self.mint(aud="https://other.example.test"))

    def test_a_token_from_another_issuer_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(self.mint(iss="https://evil.example.test"))

    def test_a_login_token_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(self.mint(scope="site"))

    def test_an_expired_token_is_refused(self):
        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(self.mint(exp=int(time.time()) - 60))

    def test_a_token_signed_with_another_key_is_refused(self):
        forged = jwt.encode(
            jwt.decode(self.mint(), options={"verify_signature": False}),
            Ed25519PrivateKey.generate(),
            algorithm="EdDSA",
        )

        with self.assertRaises(frappe.AuthenticationError):
            exchange_frappe_cloud_token(forged)
