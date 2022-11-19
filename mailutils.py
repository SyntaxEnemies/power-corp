import smtplib, ssl
from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def create_mail_handler(sender_email: str, password: str, port: int, smtp_server: str):
    # initialize ssl context and server
    ssl_context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_server, port, context=ssl_context)

    # login
    server.login(sender_email, password)
    return server


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
