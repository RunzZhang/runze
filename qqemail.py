# Import the required modules
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL


def run():
    # QQ s smtp server
    host_server = "smtp.qq.com"
    # sender_qq is the sender's amount qq number
    sender_qq = "390282332"
    # pwd is the authorization code of QQ mailbox
    pwd = "bngozrzmzsbocafa"
    # sender mailbox
    sender_mail = "390282332@qq.com"
    # recipient mailbox
    # receiver1_email = "hlippincott@ucsb.edu"  # Enter receiver address
    receiver1_mail = "runzezhang@foxmail.com"  # Enter receiver address
    # receiver1_mail = "runzezhang@foxmail.com"  # Enter receiver address


    # The body content of the mail
    mail_content = "Hello, Python Mail: Alarm from SBC slowcontrol"
    #
    mail_title = "Highlander's Mailbox"

    try:
        # sslLogin
        smtp = SMTP_SSL(host_server)
        # set_debuglevel() is used for debugging. The parameter value is 1 to enable debug mode and 0 to disable debug mode.
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)
        # Define mail content
        msg = MIMEText(mail_content, "plain", "utf-8")
        msg["Subject"] = Header(mail_title, "utf-8")
        msg["From"] = sender_mail
        msg["To"] = receiver1_mail
        # send email
        smtp.sendmail(sender_mail, receiver1_mail, msg.as_string())
        smtp.quit()
        print("mail sent successfully")
    except Exception as e:
        print("mail failed to send")
        print(e)


if __name__ == '__main__':
    run()

    # echo
    # "${ALARM_MESSAGE}" | mail - s
    # "${ALARM_SUBJECT}" "${EMAIL_ADDRESS}"
