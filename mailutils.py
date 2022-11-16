import smtplib, ssl


class MailHandler():
    def __init__(self, sender_email, password, port, smtp_server) -> None:
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


def obfuscate_mail(mail_address):
    username, domain = mail_address.split('@')
    return '{0}*****@{1}'.format(username[0:4], domain)

