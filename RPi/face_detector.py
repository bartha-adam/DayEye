from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import os
import paho.mqtt.client as mqtt
import json
import cognitive_face as CF


rundetection = True
topic_in  = "dayeye/face/in"
topic_out = "dayeye/face/out"
camera = None
rawCapture = None
# Setup the camera
def init_camera():
	global camera
	global rawCapture
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
cmd_type = "cmd"
cmd_debug = "debug"
cmd_debug_msg = "msg"
cmd_facedetected = "face_detected"
cmd_persondetected = "person_detected"
cmd_persondetected_id = "id"
cmd_stopdetection = "stop_detection"
cmd_startdetection = "start_detection"
cmd_unknown_person = "unknown_person"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_in)
    send_debug_message("FaceDetector module connected")


def on_message(client, userdata, msg):
	print("Received msg:" + str(msg.payload))
	try:
		jsonMsg = json.loads(msg.payload)
		cmdType = jsonMsg[cmd_type]
		
		if cmdType == cmd_stopdetection:
			handle_stop_detection()
		elif cmdType == cmd_startdetection:
			handle_start_detection()
		else:
			print("Unknown command")
	except ValueError:
		print "ERROR: Unexpected values...."

def handle_stop_detection():
	global rundetection
	print("Stopping detection")
	rundetection = False
    
def handle_start_detection():
	global rundetection
	print("Starting detection")
	rundetection = True

def send_debug_message(msg):
	data = {}
	data[cmd_type] = cmd_debug
	data[cmd_debug_msg] = msg
	json_data = json.dumps(data)
	client.publish(topic_out, json_data)
	
def notify_face_detected():
	data = {}
	data[cmd_type] = cmd_facedetected
	json_data = json.dumps(data)
	client.publish(topic_out, json_data)
	
def notify_person_detected(personId):
	data = {}
	data[cmd_type] = cmd_persondetected
	data[cmd_persondetected_id] = personId
	json_data = json.dumps(data)
	client.publish(topic_out, json_data)

def notify_unknown_person():
	data = {}
	data[cmd_type] = cmd_unknown_person
	json_data = json.dumps(data)
	client.publish(topic_out, json_data)

def identify_person(frame):
	print "saving image"
	# Ugly workaround but it's fast: save the jpg to ram, then FaceAPI binding reads from RAM
	cv2.imwrite( "/tmp/frame.jpg", frame);
	
	try:
		detect_result = CF.face.detect("/tmp/frame.jpg")
		print detect_result
		print "Num of faces = " + str(len(detect_result))
		if len(detect_result) == 0:
			print "FaceAPI found no face"
			return
		face_id = detect_result[0]['faceId']
		print "FaceId=" + str(face_id)
		
		identify_result = CF.face.identify([face_id], "macadamian", 1, faceapi_identity_confidence_threshold)
		print identify_result
		
		if len(identify_result) == 0:
			print "FaceAPI did not identify any face"
			return
		
		candidates = identify_result[0]['candidates']
		if len(candidates) == 0:
			print "FaceAPI did not found any candidates"
			notify_unknown_person()
			return
		
		candidate = candidates[0]
		personId = candidate['personId']
		confidence = candidate['confidence']
		print("Identified %s person with confidence %f" %(personId, confidence))
		return personId
		
	except CF.util.CognitiveFaceException as e:
		print "ERROR FaceAPI: " + str(e)
	
	return None
	

def handle_face_detected(frame):
	notify_face_detected()
	person_id = identify_person(frame)
	if person_id != None:
		notify_person_detected(person_id)


# Setup MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start() 

# Setup FaceAPI
faceapi_key = '0118754ef3d3423a91a28c21fab6e342'
faceapi_baseurl = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'
faceapi_identity_confidence_threshold = 0.5
CF.Key.set(faceapi_key)
CF.BaseUrl.set(faceapi_baseurl)

init_camera()

### Main ######################################################################

# Capture frames from the camera
while(True):
	for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
		if rundetection == False:
			camera.close()
			break
			
		image = frame.array
		gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
		faces = face_cascade.detectMultiScale( gray )
		
		if len(faces) > 0:
			handle_face_detected(image)
		
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
	
	# Wait while the detection is enabled again
	while rundetection == False:
		time.sleep(1)
	# Then init the camera again and continue capture
	init_camera()
