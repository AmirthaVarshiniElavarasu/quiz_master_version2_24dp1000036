import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = "quizmasterV2@donotreply.in"
SENDER_PASSWORD = ""

def send_email(to_address, subject, message, content = "html", attachment_file = None):  
    msg = MIMEMultipart()
    msg['From'] = SENDER_ADDRESS
    msg['To'] = to_address
    msg['Subject'] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    
    s = smtplib.SMTP(host = SMTP_SERVER_HOST, port = SMTP_SERVER_PORT)
    s.send_message(msg)
    s.quit()

    return True



