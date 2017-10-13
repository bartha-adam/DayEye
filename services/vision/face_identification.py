# This module uses Azure Cognitive Sevices to identify a person in the incomming frame
# In case face is found message is published to DayEye main topic
# ex msg: 
# { 
#   "cmd": "person",
#   "data": 
#       { "personId": "574972a0-c638-4c0c-936d-85a5a28f7904", "userData": null, "name": "abartha@macadamian.com", "persistedFaceIds": ["249a65e8-c63c-4305-aa49-90306c1f9ca7", "656024b4-9d5c-40ea-b611-1a22e373ddef", "9d92f861-7d70-4d46-ba49-e10229e5c7e6", "d4534754-d8c1-41cd-8bb0-04a2526490e2", "ffac10ef-5586-4303-810e-030acc87eb4b"]}
# }

import os
import sys
import StringIO
import numpy as np
import paho.mqtt.client as mqtt
import time
import cognitive_face as CF
from struct import *
from common import config
from common import topics
from common import messages
from threading import Thread
from PIL import Image

processing_frame = False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code %s" %(str(rc)))
    messages.send_debug_message(client, module_name, "connected")
    client.subscribe(local_faces_topic)


def on_message(client, userdata, msg):
    print("Received message from topic %s with payload size = %d b" %(msg.topic, len(msg.payload)))
    if msg.topic == local_faces_topic:
        process_local_faces_message(msg)
        

def process_local_faces_message(msg):
    global processing_frame
    if processing_frame == True:
        print("Skip frame")
        return
    processing_frame = True
    (frame_metadata, frame) = messages.parse_frame(msg.payload)
    frame_width = frame_metadata["frame"]["width"];
    frame_height = frame_metadata["frame"]["height"]
    frame_id = frame_metadata["frame"]["id"]
    if "faces" in frame_metadata:
        # metadata contains face info, probably this frame is comming from local face recongnition module
        faces = frame_metadata["faces"]
    else:
        # metadata contains no faces info, this might be a frame coming directly from the recording module
        faces = []
    
    print("Received frame %d containing %d face w=%d h=%d" %(frame_id, len(faces), frame_width, frame_height))

    print("DEBUG frame format is %s" % (type(frame)))
    frame = np.frombuffer(frame, dtype='uint8', count=frame_width * frame_height * 3 , offset=0)
    frame = np.reshape(frame, (frame_height, frame_width, 3))
    thread = Thread(target = process_frame, args = (frame, frame_metadata))
    thread.start()


def process_frame(frame, frame_metadata):
    global processing_frame
    try:
        #img.save("/tmp/faces.jpg", format='JPEG')

        # Save frame as JPEG in memory
        img = Image.fromarray(np.asarray(frame), 'RGB')
        output = StringIO.StringIO()
        img.save(output, format='JPEG')
        output.seek(0) # restore the stream, so CF API will read from beginning

        # Sample result from CF.face.detect:
        # [{u'faceId': u'27a6f5ec-92de-46ec-be61-9a76b5b38cf0', u'faceRectangle': {u'width': 100, u'top': 174, u'height': 100, u'left': 180}}]
        detect_result = CF.face.detect(output)
        print("detect_result=%s" %(detect_result))
        
        face_ids = [face['faceId'] for face in detect_result]
        print("extracted faceIds=%s" % (face_ids))

        # Sample result from CF.face.identify:
        # [{u'faceId': u'de522e65-7327-4758-ae33-24964cedf190', u'candidates': [{u'personId': u'574972a0-c638-4c0c-936d-85a5a28f7904', u'confidence': 0.60053}]}]
        identify_result = CF.face.identify(face_ids, faceapi_group_name, 1, faceapi_identity_confidence_threshold)
        print("identify_result=%s (%s)" %(identify_result, type(identify_result)))

        person_ids = []
        for face in identify_result:
            # Find and store the best candidate personIds
            candidates = face["candidates"]
            best_candidate = max(candidates, key=lambda item: item["confidence"])
            person_ids.append(best_candidate["personId"])

        print("Person_ids=%s" % (person_ids))
        for person_id in person_ids:
            # Sample person data:
            # "data": {"personId": "574972a0-c638-4c0c-936d-85a5a28f7904", "userData": null, "name": "abartha@macadamian.com", "persistedFaceIds": ["249a65e8-c63c-4305-aa49-90306c1f9ca7", "656024b4-9d5c-40ea-b611-1a22e373ddef", "9d92f861-7d70-4d46-ba49-e10229e5c7e6", "d4534754-d8c1-41cd-8bb0-04a2526490e2", "ffac10ef-5586-4303-810e-030acc87eb4b"]}
            person_data = get_person_data(person_id)
            cmd = messages.compose_person_identified(person_data);
            print("Publish %s" % (cmd))
            client.publish(topics.MAIN_TOPIC, cmd)

            # TODO remove this two lines
            say_cmd = messages.compose_say("Hi %s" % person_data["name"])
            client.publish("dayeye/t2s/in", say_cmd)

        print("Finished processing frame")
        processing_frame = False

    except Exception as e:
        print("Error while processing frame: %s" % e)

    processing_frame = False   


def get_person_data(person_id):
    print("Requesting data for persion with id=%s" %(person_id))
    person_info_response = CF.person.get(faceapi_group_name, person_id)
    print("Obtained person info: %s" % (person_info_response))
    return person_info_response

module_name = os.path.basename(__file__)
camera_resolution_width  = config.get_config_value(config.CONFIG_RECORDING_RESOLUTION_WIDTH)
camera_resolution_height = config.get_config_value(config.CONFIG_RECORDING_RESOLUTION_HEIGHT)
faceapi_identity_confidence_threshold = config.get_config_value(config.CONFIG_FACEAPI_IDENTITY_CONFIDENCE_THRESHOLD)
faceapi_group_name = config.get_config_value(config.CONFIG_FACEAPI_GROUP_NAME)

local_faces_topic = topics.LOCAL_FACES_TOPIC

faceapi_key = config.get_config_value(config.CONFIG_FACEAPI_KEY)
faceapi_baseurl = config.get_config_value(config.CONFIG_FACEAPI_BASEURL)
CF.Key.set(faceapi_key)
CF.BaseUrl.set(faceapi_baseurl)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever() 
