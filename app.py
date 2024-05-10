from requests import request
from flask import Flask, render_template, Response, redirect,url_for,request
from camera import VideoCamera
from flask_sqlalchemy import SQLAlchemy
import os
current_file_path = os.path.abspath(__file__)
basedir = os.path.dirname(current_file_path)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
video_stream = VideoCamera()

class Reciever(db.Model):
    email = db.Column(db.String(100),nullable=False,primary_key=True)
    def __repr__(self) -> str:
        return f"{self.email}"
process_run=True
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_email',methods=['POST'])
def save_email():
    # print(request.body)
    if request.form:
        rec=Reciever(email=request.form['email'])
        db.session.add(rec)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('index'))

@app.route('/home')
def home():
    global process_run
    global video_stream
    process_run=True
    video_stream.setcam()
    return render_template('home.html')

@app.route('/watch')
def watch():
    return render_template('watch.html')

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1',port="5000")
