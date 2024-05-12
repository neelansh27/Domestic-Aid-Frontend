import cv2
from ultralytics import YOLO
from email.message import EmailMessage
import ssl
import conf
import smtplib

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

cam=cv2.VideoCapture(0) # declaring input feed

# Intialising models
model=YOLO('yolov8m.pt')
act_model=YOLO('./runs/detect/train/weights/best.pt')
ret,frame=cam.read()
newFrame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
#Checking if a person exists in frame
results=model.predict(source=newFrame,classes=0,save=True,conf=0.5)
for result in results:
    if (not result.boxes): # this will be true if a person does not exists
        print('Person is not in image')
        # Check if any appliances are running
        ret,img=cam.read()
        newImg=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        res=act_model.predict(source=newImg,save=True,conf=0.5)
        objs=res[0].boxes
        if (objs):
            # WE WILL SEND NOTIFICATION HERE
            print('Some appliances are running')
            send_notification('neelishero@gmail.com')
        else:
            print('No appliances are running')
        break

del(cam)
