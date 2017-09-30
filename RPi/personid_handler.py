import json
import datetime
import requests
import cognitive_face as CF
import paho.mqtt.client as mqtt

topic_in  = "dayeye/face/out"
text_to_speach_topic = "dayeye/t2s/in"
cmd_type = "cmd"

cmd_debug = "debug"
cmd_debug_msg = "msg"

cmd_persondetected = "person_detected"
cmd_persondetected_id = "id"

cmd_say = "say"
cmd_say_text = "text"

cmd_unknown_person = "unknown_person"

faceapi_group_name = "macadamian"
faceapi_key = '0118754ef3d3423a91a28c21fab6e342'
faceapi_baseurl = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'

dayeye_server_baseurl = "http://172.24.10.63/DayEye/"
dayeye_server_detectedurl = dayeye_server_baseurl + "detected"

last_detected_person_name = None
last_detected_person_at = None
re_detect_time_threshold_sec = 30


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print "Subscribing to topic %s" %(topic_in)
    client.subscribe(topic_in)

def on_message(client, userdata, msg):
	print("Received msg:" + str(msg.payload))
	try:
		json_msg = json.loads(msg.payload)
		cmd = json_msg[cmd_type]
		
		if cmd == cmd_debug:
			handle_debug_command(json_msg)
		elif cmd == cmd_persondetected:
			handle_person_detected(json_msg)
		elif cmd == cmd_unknown_person:
			handle_unknown_person()
		else:
			print("Unknown command")
	except ValueError:
		print "ERROR: Unexpected values...." 
	
def handle_person_detected(json_msg):
	global last_detected_person_name
	global last_detected_person_at
	global re_detect_time_threshold_sec
	
	person_id = json_msg[cmd_persondetected_id]
	print "Detected person %s" % (person_id)
	print "Trying to obtain person info for %s" % ((person_id))
	try:
		person_info_response = CF.person.get(faceapi_group_name, person_id)
		# print person_info_response
		person_name = person_info_response["name"]
		print "Obtained name=%s" %(person_name) 
		
		if last_detected_person_name != None and last_detected_person_name == person_name:
			elapsed_from_last_detection = (datetime.datetime.now() - last_detected_person_at).total_seconds()
			if elapsed_from_last_detection < re_detect_time_threshold_sec:
				print "Elapsed only %d seconds since last detection => SKIP" % (elapsed_from_last_detection)
				return
			
		last_detected_person_name = person_name
		last_detected_person_at = datetime.datetime.now()
		
		post_data = params = {'email': person_name } # person_name is actually the id, it's the email address
		server_response = requests.post(dayeye_server_detectedurl, post_data)
		print "Received response (%d): %s" % (server_response.status_code, server_response.text)
		publish_say_cmd(server_response.text)
		
	except CF.util.CognitiveFaceException as e:
		print "Failed to get person info %s" % (str(e))

def handle_unknown_person():
	#publish_say_cmd("Yo motherfucker, go and register. Download Dan's super app. He loves android!")
	publish_say_cmd("I don't know you, please register!")
	

def handle_debug_command(json_msg):
	print("Debug msg: %s" % (json_msg[cmd_debug_msg]))
	
def publish_say_cmd(text):
	data = {}
	data[cmd_type] = cmd_say
	data[cmd_say_text] = text
	
	json_data = json.dumps(data)
	client.publish(text_to_speach_topic, json_data)

# Setup FaceAPI
CF.Key.set(faceapi_key)
CF.BaseUrl.set(faceapi_baseurl)

# Setup MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever() 



