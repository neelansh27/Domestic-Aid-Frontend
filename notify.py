import conf
import ssl
import smtplib
from email.message import EmailMessage
def send_notification(email):
    email_sender = 'adamsjohnwork@gmail.com'
    email_password = conf.data['password']

    email_receiver = 'neelishero@gmail.com' # enter email

    subject = "Something Detected"

    body = """
    An appliance is detected in the camera that is turned ON
    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    i=0
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    i+=1
