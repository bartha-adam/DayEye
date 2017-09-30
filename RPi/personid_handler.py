import json
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

faceapi_group_name = "macadamian"
faceapi_key = '0118754ef3d3423a91a28c21fab6e342'
faceapi_baseurl = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'

dayeye_server_baseurl = "http://172.24.10.63/DayEye/"
dayeye_server_detectedurl = dayeye_server_baseurl + "detected"

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
		else:
			print("Unknown command")
	except ValueError:
		print "ERROR: Unexpected values...." 
	
def handle_person_detected(json_msg):
	person_id = json_msg[cmd_persondetected_id]
	print "Detected person %s" % (person_id)
	print "Trying to obtain person info"
	try:
		person_info_response = CF.person.get(faceapi_group_name, person_id)
		print person_info_response
		person_name = person_info_response["name"]
		print "Name=%s" %(person_name)
		
		post_data = params = {'email': person_name }
		print post_data
		r = requests.post(dayeye_server_detectedurl, post_data)
		print r
		print r.text
		publish_say_cmd(r.text)
		
	except CF.util.CognitiveFaceException as e:
		print "Failed to get person info %s" % (str(e))
	
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



