import ssl
import logging
import smtplib
from pathlib import Path
from typing import List, Union
from email.message import EmailMessage
from fastapi import BackgroundTasks
from src.config import AppConfigs
from dataclasses import dataclass

@dataclass
class EmailTemplate:
    Subject: str
    Content: str

class EmailSender:
    def __init__(self):
        pass

    NoReply = '"InfinityHubs" <noreply@infinityhubs.in>'
    Operation = '"InfinityHubs" <operations@infinityhubs.in>'

class EmailClient:
    def __init__(self):
        self.port = AppConfigs.SMTP_PORT
        self.username = AppConfigs.SMTP_USER
        self.password = AppConfigs.SMTP_PASSWORD
        self.smtp_server = AppConfigs.SMTP_SERVER
        self.logger = logging.getLogger(__name__)

    def dispatch_email(self, recipients: List[str], msg: EmailMessage):
        """Send an email immediately."""
        try:
            if self.port == 465:
                # SSL connection
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg, to_addrs=recipients)
            elif self.port == 587:
                # STARTTLS connection
                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg, to_addrs=recipients)
            else:
                error_message = f"Invalid port: {self.port}. Use 465 for SSL or 587 for STARTTLS."
                self.logger.error(error_message)
                return {"status": "error", "message": error_message}

            self.logger.info("Email sent successfully!")
            return {"status": "success", "message": "Email sent successfully!"}
        except smtplib.SMTPException as smtp_error:
            error_message = f"SMTP error occurred on server {self.smtp_server}:{self.port} - {smtp_error}"
            self.logger.error(error_message)
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            self.logger.error(error_message)
            return {"status": "error", "message": error_message}

    async def notify(
        self,
        sender: str,
        subject: str,
        message: str,
        recipient: Union[str, List[str]],
        background_tasks : BackgroundTasks = None,
        html_content: bool = True,
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None,
        attachments: List[Path] = None,
    ):
        """Schedule an email to be sent in the background."""
        if not all([subject, sender, recipient, message]):
            error_message = "Subject, sender, recipient, and message are required."
            self.logger.error(error_message)
            return {"status": "error", "message": error_message}

        # Create the email message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipient) if isinstance(recipient, list) else recipient

        if cc:
            msg['Cc'] = ', '.join(cc) if isinstance(cc, list) else cc

        # Add the body content
        msg.set_content(message, subtype = 'html' if html_content else 'plain')

        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                if not attachment.exists() or not attachment.is_file():
                    error_message = f"Attachment not found: {attachment}"
                    self.logger.error(error_message)
                    return {"status": "error", "message": error_message}
                with attachment.open('rb') as file:
                    file_data = file.read()
                    file_name = attachment.name
                    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Determine all recipients including `bcc`
        recipients = [recipient] if isinstance(recipient, str) else recipient
        if cc:
            recipients += [cc] if isinstance(cc, str) else cc
        if bcc:
            recipients += [bcc] if isinstance(bcc, str) else bcc

        # Trigger email sending in the background
        if background_tasks is not None:
            background_tasks.add_task(self.dispatch_email, recipients, msg)
            return "Your email has been successfully scheduled for background delivery."
        else:
            self.dispatch_email(recipients, msg)
            return "Email send request dispatched for processing."

class EmailTemplates:

    @staticmethod
    def load(template_name):
        template = EmailTemplates._TemplateDataset.get(template_name)
        if template:
            return EmailTemplate(
                Subject=template.get("Subject", ""),
                Content=template.get("Content", "")
            )
        return None


    _TemplateDataset = {
        "Identity_Activation": {
            "Subject": "Let's Confirm & Connect 🚀",
            "Content": """
                <!DOCTYPE html>
                <html style="font-weight: 400">
                <head style="font-weight: 400">
                  <meta charset="utf-8" style="font-weight: 400">
                  <meta name="viewport" content="width=device-width, initial-scale=1" style="font-weight: 400">
                  <style type="text/css" style="font-weight: 400">
                    @import url(https://fonts.googleapis.com/css?family=Lato:400,700);
                  </style>
                </head>
                <body class="" style='font-weight: 400; background-image: url(https://s1.sentry-cdn.com/_static/5a7fde23ebbabcb14828e3b3a52b147b/sentry/images/email/sentry-pattern.png); width: 100%; font-size: 16px; font-family: "Lato", "Helvetica Neue", helvetica, sans-serif; background-color: #fff; color: #2f2936; -webkit-font-smoothing: antialiased; margin: 0; padding: 0'>
                  <div class="preheader" style="font-weight: 400; display: none; font-size: 0; max-height: 0; line-height: 0; mso-hide: all; padding: 0"></div>
                  <table class="main" style='font-weight: 400; width: 100%; border-collapse: separate; font-size: 16px; font-family: "Lato", "Helvetica Neue", helvetica, sans-serif; background-color: #fff; color: #2f2936; -webkit-font-smoothing: antialiased; max-width: 700px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); border-radius: 4px; border: 1px solid #c7d0d4; border-spacing: 0; margin: 15px auto; padding: 0'>
                    <tr style="font-weight: 400">
                      <td style="font-weight: 400; text-align: center; margin: 0; padding: 0">
                        <div class="header" style="font-weight: 400; font-size: 14px; border-bottom: 1px solid #dee7eb; padding: 23px 0">
                          <div class="container" style="font-weight: 400; max-width: 600px; text-align: left; margin: 0 auto; padding: 0 20px">
                            <h1 style="font-weight: normal; font-size: 38px; line-height: 42px; color: #000; letter-spacing: -1px; margin: 0; padding: 0">
                              <a href="https://infinityhubs.in" style="font-weight: 500; color: #000000; text-decoration: none">InfinityHubs</a>
                            </h1>
                          </div>
                        </div>
                      </td>
                    </tr>
                    <tr style="font-weight: 400">
                      <td style="font-weight: 400; text-align: center; margin: 0; padding: 0">
                        <div class="container" style="font-weight: 400; max-width: 600px; text-align: left; margin: 0 auto; padding: 0 20px">
                          <div class="inner" style="font-weight: 400; background-color: #fff; padding: 30px 0 20px">
                            <h3 style="font-weight: 700; font-size: 18px; margin: 0 0 20px">Hi ##NAME##,</h3>
                            <p style="font-weight: 400; font-size: 16px; line-height: 24px; margin: 0 0 15px">Thanks for signing up for <strong>InfinityHubs Connected Enterprises!</strong></p>
                            <p style="font-weight: 400; font-size: 16px; line-height: 24px; margin: 0 0 15px">Please confirm your email (<strong>##EMAIL##</strong>) by clicking the button below.</p>
                            <p style="font-weight: 400; font-size: 16px; line-height: 24px; margin: 0 0 15px"><a href="##LINK##" class="btn" style="font-weight: 600; color: #fff; text-decoration: none; background-color: #6C5FC7; border: 1px solid #413496; box-shadow: 0 2px 0 rgba(0, 0, 0, 0.08); line-height: 18px; border-radius: 4px; display: inline-block; font-size: 16px; padding: 8px 15px">Confirm</a></p>
                            <p style="font-weight: 400; font-size: 16px; line-height: 24px; margin: 0 0 15px">This link will expire in <strong>24 hours</strong>. If you did not sign up for an account, no further action is required, and you can safely disregard this email.</p>
                          </div>
                        </div>
                        <div class="container" style="font-weight: 400; max-width: 600px; text-align: left; margin: 0 auto; padding: 0 20px">
                          <div class="footer" style="font-weight: 400; border-top: 1px solid #E7EBEE; padding: 35px 0">
                            <a href="https://infinityhubs.in" style="font-weight: 500; color: #687276; text-decoration: none; float: right">Home</a>
                            <a href="#" style="font-weight: 500; color: #687276; text-decoration: none">Notification Settings</a>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </table>
                </body>
                </html>
            """
        }
    }


