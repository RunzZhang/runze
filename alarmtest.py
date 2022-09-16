import smtplib, ssl

port = 465  # For SSL
authorization_code="bngozrzmzsbocafa"
smtp_server = "smtp.gmail.com"
sender_email = "390282332@qq.com"  # Enter your address
receiver1_email = "hlippincott@ucsb.edu"  # Enter receiver address
receiver2_email = "cdahl@northwestern.edu"  # Enter receiver address
password = input("Type your password and press enter: ")
message = """\
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver1_email, message)
    server.sendmail(sender_email, receiver2_email, message)