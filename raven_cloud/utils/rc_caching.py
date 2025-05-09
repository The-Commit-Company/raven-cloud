import frappe

def get_push_tokens_for_user(user_id):
	"""
	Gets the push tokens for a user
	"""

	def _get_push_tokens_for_user(user_id):
		return frappe.get_all(
			"RC Site User Token", filters={"user": user_id}, fields=["fcm_token"]
		)

	return frappe.cache().hget("rc:push_tokens_for_user", user_id, _get_push_tokens_for_user)

def clear_push_tokens_for_user_cache(user_id):
	frappe.cache().hdel("rc:push_tokens_for_user", user_id)