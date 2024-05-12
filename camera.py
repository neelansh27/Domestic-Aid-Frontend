import cv2
from notify import send_notification
from ultralytics import YOLO
class VideoCamera(object):
    def __init__(self,email):
        self.video = cv2.VideoCapture(0)
        self.model=YOLO('yolov8m.pt')
        self.act_model=YOLO('best.pt')
        # print('class',email)
        self.email = email

    def __del__(self):
        self.video.release()        

    def get_frame(self):
        ret, frame = self.video.read()
        results=self.model.predict(source=frame,classes=0,save=True,conf=0.5)
        for result in results:
            if (not result.boxes): # this will be true if a person does not exists
                print('Person is not in image')
                # Check if any appliances are running
                # newImg=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                res=self.act_model.predict(source=frame,save=True,conf=0.5)
                if (res[0].boxes):
                    # WE WILL SEND NOTIFICATION HERE
                    print('Some appliances are running')
                    print(self.email)
                    send_notification(self.email)
                else:
                    print('No appliances are running')
                # ret, jpeg = cv2.imencode('.jpg', res)
                # return jpeg.tobytes()
                break

        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()
    def stop(self):
        self.video.release()
