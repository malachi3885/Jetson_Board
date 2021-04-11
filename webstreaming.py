from imutils.video import VideoStream , WebcamVideoStream
import threading
import argparse
import imutils
import time
import cv2
from flask import Flask, render_template, redirect, flash, url_for, session, Response, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from crontab import CronTab
from scipy.spatial.distance import cdist
import numpy as np
import datetime
from faceDetectorAndAlignment import faceDetectorAndAlignment
from faceEmbeddingExtractor import faceEmbeddingExtractor
import requests
import json

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

inputStream = cv2.VideoCapture(0)
time.sleep(2.0)

# Add from satit file
app.config['SECRET_KEY'] = 'tempKey'

cron = CronTab(user='root')

detector = faceDetectorAndAlignment('models/faceDetector.onnx', processScale=0.5)
embeddingExtractor = faceEmbeddingExtractor('models/r100-fast-dynamic.onnx')

class setupForm(FlaskForm):
	date = StringField('Date: ')
	starttime = StringField('Begin: ')
	endtime = StringField('End: ')
	submit = SubmitField('Submit')

class setupFormSubmit(FlaskForm):
	submit = SubmitField('Submit')

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

#TODO ลบหน้าแรกไปไว้ในคอม
"""
@app.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'POST':
		room = request.form['room']
		#TODO redirects to ห้อง 
		# return redirect('http://www.google.com')
		return redirect(url_for('choose_action', room=room))
	else:
		return render_template('main.html')
"""

@app.route('/choose_action_<room>')
def choose_action(room):
	return  render_template('choose_action.html', room=room)

@app.route('/clock', methods=['GET','POST'])
def set_clock():
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
		
		return redirect(url_for('set_clock'))
		
	return render_template('clock.html', form=form, data=tabledata)

def gen():
    while True:
        isFrameOK, inputFrame = inputStream.read()
        frame = imutils.resize(inputFrame,width=800)
        (flag, encoedImage) = cv2.imencode(".jpg",frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoedImage) + b'\r\n')

@app.route('/room<room>/course<course>/live', methods=['POST', 'GET'])
def live(room, course):
	students = list()
	if request.method == 'POST':
		if request.form['button'] == 'check':
			faces = np.load('./storeEmbedding/embedding.npy', allow_pickle=True)
			if (faces.size!=0):
				name = np.load('./storeEmbedding/name.npy', allow_pickle=True)
				ids = np.load('./storeEmbedding/id.npy', allow_pickle=True)

				
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
						distance = distance.reshape(distance.shape[1],distance.shape[0])
						### Draw face ##
						for faceIdx, faceBox in enumerate(faceBoxes):
							### find min distance
							dis_face = distance[faceIdx]
							# print(dis_face)
							if np.min(dis_face) < 0.9:
								student['id'] = ids[np.where(dis_face == np.min(dis_face))[0]][0]
								student['name'] = name[np.where(dis_face == np.min(dis_face))[0]][0]
								students.append(student)


		elif request.form['button'] == 'clear':
			faces = np.load('./storeEmbedding/embedding.npy', allow_pickle=True)

			print('mickey')
			print(faces.size)
			
			students.clear()
		elif request.form['butotn'] == 'back' :
			redirect(url_for('course', room=room))

	return render_template('live_stream.html', room=room, course=course, students=students)


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/room<room>/choose_course', methods=['POST', 'GET'])
def course(room):
    if request.method == 'POST':
        count = True
        course = request.form['course']
        #TODO ใส่courseให้ถูก
        url = 'https://face-senior.herokuapp.com/fetchStudent'

        payload = {'course_id' : course, 'semester': 2, 'acedamic_year': 2564}

        res = requests.post(url, json=payload, allow_redirects=True)
        result = json.loads(res.content)
        if (result['course'] == 'not found this course'):
            print('abc')
            embed = []
            names = []
            ids = []

            np.save('./storeEmbedding/embedding.npy', np.array([]))
            np.save('./storeEmbedding/name.npy', np.array([]))
            np.save('./storeEmbedding/id.npy', np.array([]))

        else :
            print('def')
            for student in result['student']:
                print(student['student_first_name'])
                if count :
                    embed = []
                    names = []
                    ids = []
                    np.save('./storeEmbedding/embedding.npy', np.array([]))
                    np.save('./storeEmbedding/name.npy', np.array([]))
                    np.save('./storeEmbedding/id.npy', np.array([]))

                else:
                    embed = np.load('./storeEmbedding/embedding.npy', allow_pickle=True)         
                    names = np.load('./storeEmbedding/name.npy', allow_pickle=True)
                    ids = np.load('./storeEmbedding/id.npy', allow_pickle=True)

                embed = np.append(embed, [student['embedded_face']])
                np.save('./storeEmbedding/embedding.npy', embed)

                names = np.append(names, [student['student_first_name']])
                np.save('./storeEmbedding/name.npy', names)

                ids = np.append(ids, [student['student_id']])
                np.save('./storeEmbedding/id.npy', ids) 

                count = False
        return redirect(url_for('live', room=room, course=course))
    else:
        url = 'https://face-senior.herokuapp.com/fetchCourse'
        payload = {'semester': 2, "acedamic_year": 2564 }

        res = requests.post(url, json=payload, allow_redirects=True)

        result = json.loads(res.content)

        return render_template('choose_course.html', courses=result['courses'])


# ลบออก
# @app.route("/")
# def index():
# 	# return the rendered template
# 	return render_template("index.html")

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
inputStream.stop()
