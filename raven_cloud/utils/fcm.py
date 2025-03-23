import frappe
import firebase_admin
import json

def get_app():
    """
    Fetch the firebase app instance
    Check if the app is already initialized, if not, initialize it
    """
    app = None
    try:
        app = firebase_admin.get_app(name="Raven")
    except:
        pass
    if not app:
        print("Initializing firebase app")
        fcm_settings = frappe.get_cached_doc("RC FCM Settings")
        if not fcm_settings.firebase_admin_credential:
            frappe.throw("Firebase Configuration is not set")
        credential = firebase_admin.credentials.Certificate(json.loads(fcm_settings.firebase_admin_credential))
        app =firebase_admin.initialize_app(credential, name="Raven")

    return app
