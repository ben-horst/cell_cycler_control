import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage


class Gmail:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/gmail.send"]
        self.creds = None

    def get_creds(self):
        if os.path.exists("./core/token.json"):
            self.creds = Credentials.from_authorized_user_file("./core/token.json", self.scopes)
        if not self.creds or not self.creds.valid:
            print(self.creds.valid)
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("./core/credentials.json", self.scopes)
                self.creds = flow.run_local_server(port=0)
            with open("./core/token.json", "w") as token:
                token.write(self.creds.to_json())

    def send_email(self, to, subject, content):
        self.get_creds()
        try:
            service = build("gmail", "v1", credentials=self.creds)
            message = EmailMessage()
            message.set_content(content)
            message["To"] = to
            message["From"] = "ben.horst@flyzipline.com"
            message["Subject"] = subject
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"raw": encoded_message}
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
        except HttpError as error:
            print(f"An error occurred: {error}")
            send_message = None
        return send_message

