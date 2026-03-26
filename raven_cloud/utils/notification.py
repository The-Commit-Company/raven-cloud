import frappe

def sanitize_fcm_data(data_dict):
    """
    Sanitize data for FCM by converting None values to empty strings.
    FCM requires all data values to be strings.
    """
    if not data_dict:
        return None

    sanitized = {}
    for key, value in data_dict.items():
        # convert None to empty string, everything else to string
        sanitized[key] = str(value) if value is not None else ""
    return sanitized


def get_background_job_id(messages, site_name: str) -> str:
    first = (messages or [{}])[0]
    data = first.get("data") or {}

    channel_id = data.get("channel_id") or first.get("channel_id") or "no-channel"
    message_id = data.get("message_id") or first.get("message_id") or "no-message"

    return f"rc_push_{frappe.scrub(site_name)}_{frappe.scrub(channel_id)}_{frappe.scrub(message_id)}"
