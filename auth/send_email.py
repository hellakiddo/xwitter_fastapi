import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_confirmation_email(email, code):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'ams800v@gmail.com'
    smtp_password = 'drbb ulgh fnod tpsg'

    sender_email = 'Xwitter'
    subject = 'Confirmation Email'
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject

    body = f'Ваш код тут: {code}'
    message.attach(MIMEText(body, 'plain'))
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, email, message.as_string())
