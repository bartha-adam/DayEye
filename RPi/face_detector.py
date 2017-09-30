from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import os
import paho.mqtt.client as mqtt
import json

rundetection = True

# Setup the camera
camera = PiCamera()
camera.resolution = ( 320, 240 )
camera.framerate = 60
rawCapture = PiRGBArray( camera, size=( 320, 240 ) )

# Load a cascade file for detecting faces
face_cascade = cv2.CascadeClassifier( 'lbpcascade_frontalface_improved.xml' )
#face_cascade = cv2.CascadeClassifier( 'lbpcascade_frontalface.xml' ) 

t_start = time.time()
fps = 0

# MQTT handlers
cmd_type = "cmd_type"
cmd_debug = "debug"
cmd_debug_msg = "msg"
cmd_facedetected = "face_detected"
cmd_stopdetection = "stop_detection"
cmd_startdetection = "start_detection"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)
    #client.publish(topic, "FaceDetector module connected");
    send_debug_message("FaceDetector module connected")


def on_message(client, userdata, msg):
	print("Received msg:" + str(msg.payload))
	try:
		jsonMsg = json.loads(msg.payload)
		cmdType = jsonMsg[cmd_type]
		
		if cmdType == cmd_stopdetection:
			handleStopDetection()
		elif cmdType == cmd_startdetection:
			handleStartDetection()
		else:
			print("Unknown command")
	except ValueError:
		print "ERROR: Unexpected values...."

def handleStopDetection():
	global rundetection
	print("Stopping detection")
	rundetection = False
    
def handleStartDetection():
	global rundetection
	print("Starting detection")
	rundetection = True

def send_debug_message(msg):
	data = {}
	data[cmd_type] = cmd_debug
	data[cmd_debug_msg] = msg
	json_data = json.dumps(data)
	client.publish(topic, json_data)
	
def send_face_detected():
	data = {}
	data[cmd_type] = cmd_facedetected
	json_data = json.dumps(data)
	client.publish(topic, json_data)

# Setup MQTT
topic = "DayEye"
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start() 



### Main ######################################################################

# Capture frames from the camera
for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
    if rundetection == False:
		time.sleep(1)
		rawCapture.truncate( 0 )
		continue
		
    image = frame.array
    gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
    faces = face_cascade.detectMultiScale( gray )
    
    if len(faces) > 0:
		send_face_detected()
    
    # Draw a rectangle around every face and move the motor towards the face
    for ( x, y, w, h ) in faces:
    
        cv2.rectangle( image, ( x, y ), ( x + w, y + h ), ( 100, 255, 100 ), 2 )
        cv2.putText( image, "Face No." + str( len( faces ) ), ( x, y ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )
    
        tx = x + w/2
        ty = y + h/2

    # Calculate and show the FPS
    fps = fps + 1
    sfps = fps / ( time.time() - t_start )
    cv2.putText( image, "FPS : " + str( int( sfps ) ), ( 10, 10 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )    
    print "FPS: " + str( int( sfps ) ) + " FaceCnt: " + str(len(faces))
    
    cv2.imshow( "Frame", image )
    
    cv2.waitKey( 1 )

    # Clear the stream in preparation for the next frame
    rawCapture.truncate( 0 )
