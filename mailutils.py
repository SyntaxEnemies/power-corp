import smtplib, ssl
from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class MailHandler():
    def __init__(self, sender_email: str, password: str, port: int, smtp_server: str) -> None:
        # mail credentials to use for sending
        self.sender_email = sender_email
        self.password = password

        # server details
        self.port = port
        self.smtp_server = smtp_server

    def __enter__(self) -> 'SMTP_SSL':
        # initialize ssl context and server
        ssl_context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.port, context=ssl_context)

        # login
        self.server.login(self.sender_email, self.password)
        return self.server

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.server.close()

        if exc_type:
            raise exc_type(exc_value)


def obfuscate_mail_address(mail_address: str) -> str:
    username, domain = mail_address.split('@')
    return '{0}*****@{1}'.format(username[0:4], domain)

def compose_html_mail(sender: str, receiver: str, subject: str, template: str, **format_spec) -> str:
    message = MIMEMultipart('alternative')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject

    # html attachment
    html_content = render_template(template, **format_spec)
    # print(html_content)
    html = MIMEText(html_content, 'html')
    message.attach(html)

    return message.as_string()
