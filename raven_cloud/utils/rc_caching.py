import frappe

def get_push_tokens_for_user(user_id, site_name: str):
    """
    Gets the push tokens for a user
    """

    site_user = frappe.db.exists(
        "RC Site User", {"user_id": user_id, "site": site_name}
    )

    if not site_user:
        return []

    def _get_push_tokens_for_user():
        """
        Get the push tokens for a user
        """
        # check if the user exists, if not, return empty list

        all_tokens = frappe.get_all(
            "RC Site User Token", filters={"user": site_user}, pluck="fcm_token"
        )

        if not all_tokens:
            return []

        rc_invalid_tokens = frappe.qb.DocType("RC Invalid Tokens")

        # we only need to return the valid tokens and not the invalid tokens for this site user
        invalid_tokens = (
            frappe.qb.from_(rc_invalid_tokens)
            .select(rc_invalid_tokens.invalid_token)
            .where(rc_invalid_tokens.site == site_name)
            .where(rc_invalid_tokens.invalid_token.isin(all_tokens))
            .run(pluck=True)
        )
        valid_tokens = [token for token in all_tokens if token not in invalid_tokens]

        return valid_tokens

    return frappe.cache().hget(
        "rc:push_tokens_for_user", site_user, _get_push_tokens_for_user
    )

def clear_push_tokens_for_user_cache(user_id):

	frappe.cache().hdel("rc:push_tokens_for_user", user_id)