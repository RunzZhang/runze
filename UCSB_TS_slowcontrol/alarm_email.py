import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, smtp_username, smtp_password):
    # Create a MIMEText object to represent the email body
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Establish a connection to the SMTP server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        # Login to your Gmail account
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

# Replace the following placeholders with your actual information
sender_email = "runzezhang@ucsb.edu"
receiver_email = "runzezhang26@outlook.com"
subject = "Henry's panel"
body = "This is a test email sent using Python and Gmail's SMTP server."
smtp_server = "smtp.gmail.com"
smtp_port = 465
smtp_username = "runzezhang@ucsb.edu"
smtp_password = "qsdjwlgtleuwcvqe"

# Call the function to send the email
send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, smtp_username, smtp_password)