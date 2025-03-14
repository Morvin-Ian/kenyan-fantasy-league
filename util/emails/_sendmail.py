import logging
import smtplib
from threading import Thread, Event

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from rest_framework.exceptions import APIException

logger = logging.getLogger("Email sending")


class EmailThread(Thread):
    """
        Due to system freeze when sending mails. We create a custom thread to handle mail sending.
        This enables multithreading and ensures the platform does not freeze when sending bulk emails.

    """

    def __init__(self, subject: str, template_name: str, context: dict, recipient_list: list, reply_to: list,
                 mail_action: str, attachments):
        self.mail_action = mail_action
        self.subject = subject
        self.recipient_list = recipient_list
        self.template_name = template_name
        self.context = context
        self.reply_to = reply_to
        self.attachments = attachments
        self.success = False
        self.stop_event = Event()
        Thread.__init__(self)

    def run(self):
        try:
            html_content = render_to_string(self.template_name, self.context)
            if self.mail_action is not None and self.mail_action == 'bulk_certificate':
                connection = get_connection()

                emails = []
                for recipient, attachment in self.attachments:
                    msg = EmailMessage(
                        self.subject, html_content, settings.DEFAULT_FROM_EMAIL, [recipient], reply_to=self.reply_to
                    )
                    msg.content_subtype = "html"
                    msg.attach_file(attachment)
                    emails.append(msg)

                connection.send_messages(emails)
            else:
                # Use a reusable email connection for efficiency
                with get_connection() as connection:
                    msg = EmailMessage(
                        self.subject,
                        html_content,
                        settings.DEFAULT_FROM_EMAIL,
                        self.recipient_list,
                        reply_to=self.reply_to,
                        connection=connection
                    )
                    msg.content_subtype = "html"
                    msg.send(fail_silently=True)
            self.success = True
        except smtplib.SMTPRecipientsRefused as e:
            raise APIException("Failed to send email to some recipients: %s", e.recipients)
        except Exception as e:
            raise APIException(f"Email sending failed: {str(e)}")

    def stop_thread(self):
        self.stop_event.set()


def send_mail(subject, template_name, context, recipient_list, reply_to, mail_action: str = None,
              attachments=None) -> bool:
    email_thread = EmailThread(subject, template_name, context, recipient_list, reply_to, mail_action, attachments)
    email_thread.start()
    email_thread.join(timeout=30)

    if email_thread.is_alive():
        email_thread.stop_thread()
        logger.error("Email sending timed out")
        return False
    elif email_thread.success:
        logger.info("Email sent successfully")
        return True
    else:
        logger.error("Email sending failed")
        return False
