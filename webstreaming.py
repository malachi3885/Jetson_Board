from imutils.video import VideoStream , WebcamVideoStream
import threading
import argparse
import imutils
import time
import cv2
from flask import Flask, render_template, redirect, flash, url_for, session, Response, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from crontab import CronTab
from scipy.spatial.distance import cdist
import numpy as np
import datetime
from faceDetectorAndAlignment import faceDetectorAndAlignment
from faceEmbeddingExtractor import faceEmbeddingExtractor
import pandas as pd
import requests
import json
import os

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

#TODO
inputStream = cv2.VideoCapture(0)
time.sleep(2.0)

# Add from satit file
app.config['SECRET_KEY'] = 'tempKey'

#TODO
cron = CronTab(user='mickey')

IPmapping = {'319':'192.168.86.35','412':'192.168.1.53'}

detector = faceDetectorAndAlignment('models/faceDetector.onnx', processScale=0.5)
embeddingExtractor = faceEmbeddingExtractor('models/r100-fast-dynamic.onnx')

class setupForm(FlaskForm):
	date = StringField('Date: ')
	starttime = StringField('Begin: ')
	endtime = StringField('End: ')
	submit = SubmitField('Submit')

class excelForm(FlaskForm):
    file = FileField('csv file')
    submit = SubmitField('Upload')
	
class setupFormSubmit(FlaskForm):
	submit = SubmitField('Submit')

def to_send(df):
    data = dict()
    for index, row in df.iterrows():
        if get_IP(row['room']) in data:
            data[get_IP(row['room'])].append([row['room'],row['course_id'],row['course_name'],row['section'],row['date'],row['begin'],row['end']])
        else:
            data[get_IP(row['room'])] = []
            data[get_IP(row['room'])].append([row['room'],row['course_id'],row['course_name'],row['section'],row['date'],row['begin'],row['end']])
    return data
	
def validatetime(hour, minute, endhour, endminute, day, month):
	hour = int(hour)
	minute = int(minute)
	endhour = int(endhour)
	endminute = int(endminute)
	day = int(day)
	month = int(month)
	
def formatdatetime(x):
	if x < 10:
		return f'0{x}'
	else:
		return str(x)
#TODO

def get_IP(room):
    return IPmapping[str(room)]

def writetime(hour, minute, endhour, endminute, day, month, n):
	hour = int(hour)
	minute = int(minute)
	endhour = int(endhour)
	endminute = int(endminute)
	day = int(day)
	month = int(month)
	if n == -5:
		if minute >= 5:
			minute -= 5
		else:
			hour -= 1
			minute += 55
	elif n == 5:
		if minute < 55:
			minute += 5
		else:
			hour += 1
			minute -= 55
	elif n == -10:
		if endminute >= 10:
			endminute -= 10
		else:
			endhour -= 1
			endminute += 50
			
	path = 'omxplayer -p /home/pi/mp3/'
	if n == 0:
		path += 'B+00.mp3'
	elif n == -1:
		path += 'E+00.mp3'
	elif n == -5:
		path += 'B-05.mp3'
	elif n == +5:
		path += 'B+05.mp3'
	else:
		path += 'E-10.mp3'
	
	if n == 0:
		s_day = formatdatetime(day)
		s_month = formatdatetime(month)
		s_hour = formatdatetime(hour)
		s_minute = formatdatetime(minute)
		s_endhour = formatdatetime(endhour)
		s_endminute = formatdatetime(endminute)
		job = cron.new(command = path, comment = f'{s_day}/{s_month} {s_hour}:{s_minute} {s_endhour}:{s_endminute}')
	else:
		job = cron.new(command = path, comment = 'notstart')
	if n == -1 or n == -10:
		job.hour.on(endhour)
		job.minute.on(endminute)
	else:
		job.hour.on(hour)
		job.minute.on(minute)
	job.dom.on(day)
	job.month.on(month)
	cron.write()






@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        username = request.form['username']
        password = request.form['password']
        payload = {"username" : username, "password": password}
        url = 'https://face-senior.herokuapp.com/login'

        res = requests.post(url, json=payload, allow_redirects=True)
        result = json.loads(res.content)
        if(result['status']=='success'):
            role = result['user']['role']
            user = result['user']
            if role == 'admin':
                session['user'] = user
                return redirect(url_for('admin_home'))
            if role == 'teacher':
                session['user'] = user
                return redirect(url_for('teacher_home'))
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/admin', methods=['GET','POST'])
def admin_home():
    if 'user' in session and session['user']['role'] == 'admin':
        if request.method == 'POST':
            session.pop('user', None)
            return redirect(url_for('login'))
        return render_template('admin_home.html')
    else :
        return redirect(url_for('login'))

@app.route('/teacher', methods=['GET','POST'])
def teacher_home():
    if request.method == 'POST':
        if request.form['button'] == 'log out':
            session.pop('user', None)
            return redirect(url_for('login'))
        elif request.form['button'] == 'Enter':
            room = request.form['room']
            return redirect(url_for('course',room=room))
    return render_template('teacher_home.html')

@app.route('/setting_clock', methods=['GET','POST'])
def setting_clock():
    if request.method == 'POST':
        if request.form['button'] == 'Enter':
            room = request.form['room']
            return redirect(url_for('set_clock',room=room))
    form = excelForm()

    if form.validate_on_submit():
        full_timetable = pd.read_csv(form.file.data)
        data = to_send(full_timetable)
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        #for i in data:
        #    requests.post(i, i.values())
        x = requests.post('http://192.168.1.53/writecron', json=data['192.168.1.53'])
        return render_template('success.html', data=data)                       

    return render_template('setting_clock.html', form=form)

@app.route('/manage_student', methods=['GET','POST'])
def manage_student():
    students = list()
    url = 'https://face-senior.herokuapp.com/getAllStudent'
    res = requests.get(url, allow_redirects=True)
    result = json.loads(res.content)
    for student in result['students']:
        students.append(dict({'id': student['student_id'], 'first_name': student['first_name'],  'last_name': student['last_name'],'Nickname': student['nick_name'],'GPAX': student['gpax']}))
    if request.method == 'POST':
        print(10112)
    
    return render_template('manage_student.html', students=students)

@app.route('/manage_course', methods=['GET','POST'])
def manage_course():
    courses = list()
    url = 'https://face-senior.herokuapp.com/getAllCourse'
    res = requests.get(url, allow_redirects=True)
    result = json.loads(res.content)
    for course in result['courses']:
        courses.append(dict({'id': course['course_id'], 'name': course['course_name'], 'section': course['section'], 'year': course['academic_year'], 'semester':course['semester'], 'ocourse_id':course['ocourse_id'], 'teacher_id':course['teacher_id']}))
    if request.method == 'POST':
        if request.form['button'] == 'Confirm':
            course_id = request.form['course-id']
            course_name = request.form['course-name']
            section = request.form['section']
            year = request.form['year']
            semester = request.form['semester']
            teacher_id = request.form['teacher-id']
            payload = {"course_id" : course_id, "section": section, "course_name": course_name, "academic_year": year, "semester": semester, "teacher_id": teacher_id}
            url = 'https://face-senior.herokuapp.com/addCourse'
            res = requests.post(url, json=payload, allow_redirects=True)
            result = json.loads(res.content)
            return redirect(url_for('manage_course'))
    return render_template('manage_course.html', courses=courses)

@app.route('/room<room>/clock', methods=['GET','POST'])
def set_clock(room):
	form = setupForm()
	
	tabledata = list()
	for job in cron:

		temp = dict()
		
		if job.comment != 'notstart':
			date, begin, end = job.comment.split()
			temp['date'] = date
			temp['begin'] = begin
			temp['end'] = end
			tabledata.append(temp)
#TODO
	
	if form.validate_on_submit():
		day, month = form.date.data.split('/')
		beginhour, beginminute = form.starttime.data.split(':')
		endhour, endminute = form.endtime.data.split(':')
		
		flash('Scheduled successfully')
		
		writetime(beginhour, beginminute, endhour, endminute, day, month, 0)
		writetime(beginhour, beginminute, endhour, endminute, day, month, -5)
		writetime(beginhour, beginminute, endhour, endminute, day, month, +5)
		writetime(beginhour, beginminute, endhour, endminute, day, month, -1)
		writetime(beginhour, beginminute, endhour, endminute, day, month, -10)
		
		return redirect(url_for('set_clock', room=room))
	
	return render_template('clock.html', form=form, data=tabledata, room=room)

def gen():
    while True:
        isFrameOK, inputFrame = inputStream.read()
        frame = imutils.resize(inputFrame,width=800)
        (flag, encoedImage) = cv2.imencode(".jpg",frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoedImage) + b'\r\n')



@app.route('/room<room>/course<course>/section<section>/live', methods=['POST', 'GET'])
def live(room, course, section):
    students = list()
    student = dict({'id': '6030631621', 'name': 'Itsara'})
    students.append(student)
    if request.method == 'POST':
        if request.form['button'] == 'Check':
            faces = np.load('./storeEmbedding/embedding.npy', allow_pickle=True)
            if (faces.size!=0):
                name = np.load('./storeEmbedding/name.npy', allow_pickle=True)
                ids = np.load('./storeEmbedding/id.npy', allow_pickle=True)
                gpax = np.load('./storeEmbedding/gpax.npy', allow_pickle=True)

                
                faces = faces.reshape((name.shape[0],512))
                isFrameOK, inputFrame = inputStream.read()
                ### save name owner
                if isFrameOK:
                    faceBoxes, faceLandmarks, alignedFaces = detector.detect(inputFrame)
                    if len(faceBoxes) > 0:
                        student = dict()
                        ### Extract embedding ###
                        extractEmbedding = embeddingExtractor.extract(alignedFaces)
                        # Compare embedding
                        distance = cdist(faces, extractEmbedding)
                        a = []
                        if len(distance):
                            for i in range(len(distance[0])):
                                b = []
                                for j in range(len(distance)):
                                    b.append(distance[j][i])
                                a.append(b)
                        distance = a

                        for faceIdx, faceBox in enumerate(faceBoxes):
                            x1, y1, x2, y2 = faceBox[0:4].astype(np.int)
                            
                            ### find min distance
                            dis_face = distance[faceIdx]
                            # print(dis_face)
                            if np.min(dis_face) < 0.9:
                                cv2.rectangle(inputFrame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                student = dict()
                                student['id'] = ids[np.where(dis_face == np.min(dis_face))[0]][0]
                                student['name'] = name[np.where(dis_face == np.min(dis_face))[0]][0]
                                gpa = gpax[np.where(dis_face == np.min(dis_face))[0]][0]
                                print('student')
                                print(student)
                                students.append(student)
                                cv2.putText(inputFrame, student['name']+ ' GPAX: ' + str(gpa), (x1,y1-5), cv2.FONT_HERSHEY_COMPLEX, 0.7,(255,255,255),2)   
                            else:
                                cv2.rectangle(inputFrame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                cv2.putText(inputFrame, 'Unknowed', (x1,y1-5), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,0,255),2) 
                            print('check')
                            # status = cv2.imwrite('./static/img.png',inputFrame)
                            # print(status)	
                        
                            
                            


        elif request.form['button'] == 'Clear':
            faces = np.load('./storeEmbedding/embedding.npy', allow_pickle=True)
            students.clear()
        elif request.form['button'] == 'Add' :
            student = dict()
            add_id = request.form['add_id']
            add_name = request.form['add_name']
            if (len(add_id) == 10 and len(add_name) > 0):
                student['id'] = add_id
                student['name'] = add_name
                students.append(student)
        elif request.form['button'] == 'Confirm' :
            url = 'https://face-senior.herokuapp.com/addAttendants'
            #TODO แก้backend
            date = datetime.date.today().strftime("%d/%m/%Y")

            add_students = list()
            for student in students:
                add_student = dict()
                add_student['student_id'] = student['id']
                add_students.append(add_student)
            payload = {"course_id" : course, "semester": 2, "date": date, "academic_year": 2564,  "students": add_students}
            res = requests.post(url, json=payload, allow_redirects=True)
            result = json.loads(res.content)
    #TODO
    # img = cv2.imread('./img.png')
    # img = os.path.join('static', 'img.png')
    # print('img', img)
    # return render_template('live_stream.html', room=room, course=course, students=students, user_img=img)
    return render_template('live_stream.html', room=room, course=course, section=section, students=students)

@app.route('/room<room>/choose_course', methods=['POST', 'GET'])
def course(room):
    if request.method == 'POST':
        if request.form['button'] == 'Enter':
            course = request.form['course']
            section = request.form['section']
            return redirect(url_for('live',room=room,course=course,section=section))
    return render_template('choose_course.html',room=room)


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')



# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)
# release the video stream pointer
#TODO
# inputStream.stop()
