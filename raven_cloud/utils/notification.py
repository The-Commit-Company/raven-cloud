# import frappe

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