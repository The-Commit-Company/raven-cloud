import re
from functools import lru_cache

import frappe
import jwt
from frappe import _
from frappe.rate_limiter import rate_limit

USER_ROLE = "Raven Cloud User"


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60)
def exchange_frappe_cloud_token(token: str) -> dict:
    """Return the API keys of the team's user. Every site of a team gets the same keys."""
    claims = verify_frappe_cloud_token(token)
    user = get_team_user(claims["sub"], claims.get("team_name") or claims["sub"])
    if not user.enabled:
        frappe.throw(_("Raven Cloud has disabled this team."), frappe.AuthenticationError)

    if not user.api_key:
        user.api_key = frappe.generate_hash(length=15)
        user.api_secret = frappe.generate_hash(length=15)
        # The caller is a guest that the signed token identifies, so no session user can save.
        user.save(ignore_permissions=True)

    return {"api_key": user.api_key, "api_secret": user.get_password("api_secret")}


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
    if frappe.db.exists("User", email):
        return frappe.get_doc("User", email)

    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": team_name,
            "send_welcome_email": 0,
            "roles": [{"role": USER_ROLE}],
        }
    )
    # The caller is a guest that the signed token identifies, so no session user can insert.
    return user.insert(ignore_permissions=True)
