"""Provide functions to help working with transactional emails."""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from socket import gaierror
from ssl import create_default_context

from flask import render_template


def create_mail_handler(sender_email: str, password: str, port: int,
                        smtp_server: str):
    """Create a SMTP object to perform email operations

    Parameters:
        - sender_email: email address to use for sending emails
        - password: password for the above email
        - port: port to use on smtp server for communicating
        - smtp_server: smtp server's name

    The SMTP object connects to the SMTP server over an SSL socket.
    """
    try:
        # initialize ssl context and server
        ssl_context = create_default_context()
        server = SMTP_SSL(smtp_server, port, context=ssl_context)

        # login
        server.login(sender_email, password)
        return server
    except gaierror as e:
        print(("[WARNING]: Socket error when creating mail handler.\n"
               "[WARNING]: Check your internet connection."))
        print(str(e))


def obfuscate_mail_addr(mail_address: str, ulimit: int=4) -> str:
    """Return a hideous form of given email address.

    Parameters:
        - mail_address: email address to be obfuscated
        - ulimit: number of username characters to include in result.

    Example:
        I: someone432@example.com
        O: some*****@exaple.com

    Only the username (characters before '@') is obfuscated.
    If ulimit is not provided, only first 4 characters are included in
    obfuscated mail.
    Emails with usernames having length less than given 'ulimit' cannot
    obfuscated, therefore returned as is.
    """
    username, domain = mail_address.split('@')
    if len(username) > ulimit:
        return '{0}*****@{1}'.format(username[0:ulimit], domain)
    return '{0}@{1}'.format(username[0:ulimit], domain)


def compose_html_mail(sender: str, receiver: str, subject: str, template: str,
                      **format_spec) -> str:
    """Construct a email message from a HTML template.

    Parameters:
        - sender: sender's email address (for header)
        - receiver: receipent's email address (for header)
        - subject: email subject (for header)
        - template: name of HTML template
        - format_spec: formatting data for the HTML template
    """
    # message header
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
