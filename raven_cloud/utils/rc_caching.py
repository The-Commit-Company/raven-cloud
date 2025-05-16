import frappe

def get_push_tokens_for_user(user_id, site_name: str):
	"""
	Gets the push tokens for a user
	"""

	site_user = frappe.db.exists("RC Site User", {"user_id": user_id, "site": site_name})

	if not site_user:
		return []

	def _get_push_tokens_for_user():
		"""
		Get the push tokens for a user
		"""
		# check if the user exists, if not, return empty list
		return frappe.get_all(
			"RC Site User Token", filters={"user": site_user}, pluck="fcm_token"
		)

	return frappe.cache().hget("rc:push_tokens_for_user", site_user, _get_push_tokens_for_user)

def clear_push_tokens_for_user_cache(user_id):

	frappe.cache().hdel("rc:push_tokens_for_user", user_id)