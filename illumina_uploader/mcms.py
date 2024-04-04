#!/usr/bin/env python

from datetime import datetime, timedelta
import json
from requests import post
from requests.auth import HTTPBasicAuth
from time import sleep


class McmsEmailService:

    def __init__(self, auth_url, client_id, client_secret, sender_email, logger):
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.sender_email = sender_email
        self.logger = logger
        self.token_obj = None

    def _post_email(self, email_url, email_request_body):
        """
        Sends email HTTP POST request.

        :return: If POST was successful
        :rtype: boolean
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token_obj["access_token"],
        }
        response = post(
            email_url, data=json.dumps(email_request_body), headers=headers
        )
        if response.status_code == 200:
            self.logger.info(
                f'Successfully sent email: {datetime.now().isoformat()}\n{json.dumps(email_request_body["email"])}'
            )
            return True
        else:
            self.logger.error(
                f'Failed to send email\nstatus:{response.status_code} - {response.text}\n{json.dumps(email_request_body["email"])}'
            )
            return False

    def _fetch_token(self):
        """
        Get and store an access token from the MCMS auth service.

        :return: If token retrieval was successful
        :rtype: boolean
        """
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": self.client_id,
            "grant_type": "client_credentials",
        }
        try:
            response = post(
                self.auth_url, data=data, headers=headers, auth=auth
            )
            if response.status_code == 200:
                response_json = response.json()
                timestamp = datetime.now().isoformat()
                response_json["timestamp_token_received"] = timestamp
                self.token_obj = response_json
                return True
            else:
                self.logger.error(
                    f"Failed to retrieve MCMS token: {response.status_code} - {response.text}"
                )
        except Exception as e:
            self.logger.error(f"Failed to retrieve MCMS token: {type(e)} - {e}")
        return False

    def _is_token_valid(self):
        """
        Checks if token exists and has not expired

        :return: If token is valid
        :rtype: bool
        """
        if not self.token_obj:
            return False

        token_timestamp = self.token_obj["timestamp_token_received"]
        token_expiry_seconds = self.token_obj["expires_in"]

        if not (token_timestamp and token_expiry_seconds):
            return False
        token_valid = False
        try:
            expired_datetime = datetime.fromisoformat(token_timestamp) + timedelta(
                seconds=token_expiry_seconds
            )
            if expired_datetime > datetime.now():
                token_valid = True
        finally:
            return token_valid

    def send_email(self, email_url, recipients, subject, body, max_retries=3):
        """
        Sends an email. 
        Handles token control and re-attempts on failures.
        """
        try:
            # Validate or refresh token before sending email
            has_sent_email = (
                self._is_token_valid() or self._fetch_token()
            ) and self._post_email(
                email_url,
                {
                    "from": self.sender_email,
                    "email": {
                        "to": recipients,
                        "subject": subject,
                        "bodyType": "text",
                        "body": body,
                        "attachments": [],
                    },
                },
            )

        except Exception as e:
            self.logger.error(f"Error sending email: {type(e)} - {e}")
        finally:
            if not (has_sent_email) and max_retries > 0:
                self.logger.info("Reattempting to send email...")
                sleep(5)
                self.send_email(email_url, recipients, subject, body, max_retries - 1)
            elif not (has_sent_email) and max_retries == 0:
                self.logger.info("Max MCMS email retries attempted.")
