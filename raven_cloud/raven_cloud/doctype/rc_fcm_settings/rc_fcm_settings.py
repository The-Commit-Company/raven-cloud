# Copyright (c) 2025, The Commit Company (Algocode Technologies Private Limited) and contributors
# For license information, please see license.txt

import json
import time

import firebase_admin
import frappe
import requests
from frappe import _
from frappe.model.document import Document


class RCFCMSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		firebase_admin_credential: DF.LongText
		firebase_client_configuration: DF.SmallText | None
		firebase_project_id: DF.Data | None
		vapid_public_key: DF.Data | None
	# end: auto-generated types

	def validate(self):
		# Ensure the firebase admin credential is a valid JSON
		try:
			json.loads(self.firebase_admin_credential)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid JSON for Firebase Admin Credential"))
		except Exception as e:
			frappe.throw(_(str(e)))

	def before_save(self):
		if not self.validate_firebase_credential():
			frappe.throw(_("Invalid Firebase Admin Credential"))
		else:
			self.generate_web_config()

	# def after_save(self):
	# 	# Clear the token cache
	# 	frappe.cache().delete_value("firebase_access_token")

	def validate_firebase_credential(self):
		firebase_admin_credential_json = json.loads(self.firebase_admin_credential)

		credential = firebase_admin.credentials.Certificate(firebase_admin_credential_json)
		app = firebase_admin.initialize_app(credential, name="Raven")
		try:
			firebase_admin.get_app(name="Raven")
			return True
		except Exception as e:
			frappe.throw(_(str(e)))
			return False
		finally:
			firebase_admin.delete_app(app)

	def generate_web_config(self):
		credential_json = json.loads(self.firebase_admin_credential)
		self.firebase_project_id = credential_json["project_id"]
		credential = firebase_admin.credentials.Certificate(credential_json)
		access_token_record = credential.get_access_token()

		url = f"https://firebase.googleapis.com/v1beta1/projects/{credential.project_id}/webApps"
		payload = {
			"displayName": "Raven"
		}
		headers = {
			"Authorization": f"Bearer {access_token_record.access_token}",
			"Content-Type": "application/json"
		}
		response = requests.post(url, json=payload, headers=headers)
		if response.status_code == 200:
			# save configuration
			response = response.json()
			operation_name = response["name"]
			firebase_application_id = ""
			# check operation status
			while True:
				url = f"https://firebase.googleapis.com/v1beta1/{operation_name}"
				headers = {
					"Authorization": f"Bearer {access_token_record.access_token}",
					"Content-Type": "application/json",
				}
				response = requests.get(url, headers=headers)
				if response.status_code == 200:
					response_json = response.json()
					if "done" in response_json and response_json["done"]:
						firebase_application_id = response_json["response"]["appId"]
						break
				time.sleep(5)

			if firebase_application_id == "":
				frappe.throw(_("Failed to register web app"))

			# fetch web config
			url = f"https://firebase.googleapis.com/v1beta1/projects/{credential.project_id}/webApps/{firebase_application_id}/config"
			headers = {
				"Authorization": f"Bearer {access_token_record.access_token}",
				"Content-Type": "application/json",
			}
			response = requests.get(url, headers=headers)
			if response.status_code == 200:
				# save configuration
				response_json = response.json()
				self.firebase_client_configuration = json.dumps(response_json)
		else:
			frappe.throw(_("Failed to register web app"))


