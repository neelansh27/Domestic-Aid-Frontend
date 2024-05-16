from requests import request
from flask import Flask, render_template, Response, redirect,url_for,request
from camera import VideoCamera
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import base64
import numpy as np
from notify import send_notification
from flask_socketio import SocketIO, emit
current_file_path = os.path.abspath(__file__)
basedir = os.path.dirname(current_file_path)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
db = SQLAlchemy(app)

class Reciever(db.Model):
    email = db.Column(db.String(100),nullable=False,primary_key=True)
    def __repr__(self) -> str:
        return f"{self.email}"
    def __len__(self):
        return len(self.email)
    
process_run=True
video_stream=None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_email',methods=['POST'])
def save_email():
    db.session.query(Reciever).delete()
    db.session.commit()
    if request.form:
        rec=Reciever(email=request.form['email'])
        db.session.add(rec)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('index'))

@app.route('/home')
def home():
    # print()
    global process_run
    global video_stream
    process_run=True
    client=Reciever.query.all()[0]
    video_stream=VideoCamera(client.email)
    return render_template('home.html')

@app.route('/watch')
def watch():
    return render_template('watch.html')
@app.route('/send_email')
def send():
    client=db.session.query(Reciever).all()[0]
    send_notification(client.email)
    return client.email

@app.get('/shutdown')
def shutdown():
    global video_stream
    global process_run
    process_run=False
    video_stream.stop()
    return redirect(url_for('home'))

def gen(camera):
    global process_run
    while process_run:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
     return Response(gen(video_stream),
                     mimetype='multipart/x-mixed-replace; boundary=frame')

def base64_to_image(base64_string):
    # Extract the base64 encoded binary data from the input string
    base64_data = base64_string.split(",")[1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Convert the bytes to numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    # Decode the numpy array as an image using OpenCV
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

@socketio.on('image')
def process_image(image):
    global video_stream
    if not video_stream:
        client=Reciever.query.all()[0]
        video_stream=VideoCamera(client.email)
    img=base64_to_image(image)
    processed_img=video_stream.process_frame(img)
    emit("processed_image", processed_img)
with app.app_context():
        db.create_all()
if __name__ == '__main__':
    socketio.run(host='127.0.0.1',port="5000")
