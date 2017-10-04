from struct import *
from common import config
from common import topics
from common import messages
import os
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import time
from threading import Thread

processing_frame = False
def on_connect(client, userdata, flags, rc):
    print "Connected with result code %s" %(str(rc))
    messages.send_debug_message(client, module_name, "connected")
    client.subscribe(frames_topic)


def on_message(client, userdata, msg):
    print "Received message from topic %s with payload size = %d b" %(msg.topic, len(msg.payload)) 
    if msg.topic == frames_topic:
        process_frame_message(msg)
        

def process_frame_message(msg):
    global processing_frame
    if processing_frame == True:
        print "Skip frame"
        return
    processing_frame = True
    (frame_metadata, frame) = messages.parse_frame(msg.payload)
    frame_width = frame_metadata["frame"]["width"];
    frame_height = frame_metadata["frame"]["height"]
    frame_id = frame_metadata["frame"]["id"]
    
    print "Received frame %d w=%d h=%d" %(frame_id, frame_width, frame_height)

    frame = np.frombuffer(frame, dtype='uint8', count=frame_width * frame_height * 3 , offset=0)
    frame = np.reshape(frame, (frame_height, frame_width, 3))

    thread = Thread(target = process_frame, args = (frame,))
    thread.start()

def process_frame(frame):
    global processing_frame
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    cv2.imwrite( "/tmp/frame.jpg", frame_gray);
    time.sleep(10)
    print "Finished processing frame"
    processing_frame = False

module_name = os.path.basename(__file__)
camera_resolution_width  = config.get_config_value(config.CONFIG_RECORDING_RESOLUTION_WIDTH)
camera_resolution_height = config.get_config_value(config.CONFIG_RECORDING_RESOLUTION_HEIGHT)

frames_topic = topics.VIDEO_STREAM_TOPIC

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever() 
