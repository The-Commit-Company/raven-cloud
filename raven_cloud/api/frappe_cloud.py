import re
from functools import lru_cache

import frappe
import jwt
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import now_datetime

from raven_cloud.api.notification import get_push_settings

USER_ROLE = "Raven Cloud User"


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def exchange_frappe_cloud_token(token: str, site_name: str) -> dict:
    """Register a Frappe Cloud site for its team. Return the team's API keys and the push
    settings. Every site of a team gets the same keys."""
    claims = verify_frappe_cloud_token(token)
    if site_name not in claims.get("hosts", []):
        frappe.throw(_("Frappe Cloud does not list {0} for this team.").format(site_name), frappe.PermissionError)

    user = get_team_user(claims["sub"], claims.get("team_name") or claims["sub"])
    if not user.enabled:
        frappe.throw(_("Raven Cloud has disabled this team."), frappe.AuthenticationError)

    claim_site(site_name, user.name)
    return {**get_api_keys(user.name), **get_push_settings()}


def verify_frappe_cloud_token(token: str) -> dict:
    issuer = frappe.conf.get("frappe_cloud_issuer")
    if not issuer:
        frappe.throw(_("Frappe Cloud sign-in is not configured."), frappe.AuthenticationError)

    try:
        signing_key = get_jwks_client(issuer).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],
            audience=frappe.utils.get_url(),
            issuer=issuer,
            options={"require": ["exp", "sub", "scope"]},
        )
    except jwt.PyJWTError as error:
        frappe.throw(_("Invalid Frappe Cloud token: {0}").format(error), frappe.AuthenticationError)

    if claims["scope"] != "team-identity":
        frappe.throw(_("Not a Frappe Cloud identity token."), frappe.AuthenticationError)

    return claims


@lru_cache
def get_jwks_client(issuer: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(f"{issuer.rstrip('/')}/api/method/central.api.jwks.get_jwks", timeout=10)


def get_team_user(team: str, team_name: str):
    """Its email is on the reserved .invalid domain, so it never receives mail."""
    email = f"{re.sub(r'[^a-z0-9]+', '-', team.lower()).strip('-')}@frappe-cloud.invalid"
    if not frappe.db.exists("User", email):
        # The caller is a guest that the signed token identifies, so no session user can insert.
        # Two sites of a new team can arrive together, so the second insert is skipped.
        frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": team_name,
                "send_welcome_email": 0,
                "roles": [{"role": USER_ROLE}],
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)

    return frappe.get_doc("User", email)


def get_api_keys(user: str) -> dict:
    """The user's keys, created once. The row lock stops two sites from creating different keys."""
    doc = frappe.get_doc("User", user, for_update=True)
    if not doc.api_key:
        doc.api_key = frappe.generate_hash(length=15)
        doc.api_secret = frappe.generate_hash(length=15)
        # The caller is a guest that the signed token identifies, so no session user can save.
        doc.save(ignore_permissions=True)

    return {"api_key": doc.api_key, "api_secret": doc.get_password("api_secret")}


def claim_site(site_name: str, owner: str) -> None:
    """Frappe Cloud vouches that the team serves the hostname, so the team takes over a site that
    another account registered, and that account's device tokens are removed."""
    current_owner = frappe.db.get_value("RC Site", site_name, "owner")
    if not current_owner:
        # The caller is a guest that the signed token identifies, so no session user can insert.
        frappe.get_doc({"doctype": "RC Site", "site": site_name}).insert(ignore_permissions=True)
    elif current_owner != owner:
        if site_users := frappe.get_all("RC Site User", filters={"site": site_name}, pluck="name"):
            frappe.db.delete("RC Site User Token", {"user": ("in", site_users)})
            frappe.db.delete("RC Site User", {"site": site_name})

    # Insert records the guest as owner, so the team's user is set here.
    frappe.db.set_value(
        "RC Site",
        site_name,
        {"owner": owner, "last_registered_on": now_datetime(), "last_registered_by": owner},
    )
