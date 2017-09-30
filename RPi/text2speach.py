import paho.mqtt.client as mqtt
import time
import json
import subprocess
from espeak import espeak

topic_out = "dayeye/t2s/out"
topic_in = "dayeye/t2s/in"
cmd_type = "cmd"
cmd_debug = "debug"
cmd_debug_msg = "msg"
cmd_say = "say"
cmd_say_text = "text"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_in)
    send_debug_message("Text2Speach module connected")


def on_message(client, userdata, msg):
	print("Received msg:" + str(msg.payload))
	try:
		json_msg = json.loads(msg.payload)
		cmd = json_msg[cmd_type]
		
		if cmd == cmd_say:
			handle_say(json_msg)
		else:
			print("Unknown command")
	except ValueError:
		print "Failed to parse JSON"

def handle_say(json_msg):
	text = json_msg[cmd_say_text]
	print "Say '" + text + "'"
	say_google(text)
	#say_espeak(text)

def say_google(text):
	result = subprocess.call(["../say.sh", text])
	if result != 0:
		print "Failed to say the text"

def say_espeak(text):
	espeak.synth(text)
  
def send_debug_message(msg):
	data = {}
	data[cmd_type] = cmd_debug
	data[cmd_debug_msg] = msg
	json_data = json.dumps(data)
	client.publish(topic_out, json_data)
	
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start() 

print 'Press Ctrl-C to quit.'
while True:
	time.sleep(1.0)
