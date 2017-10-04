from common import config
from common import topics
from common import messages
from picamera import PiCamera
from picamera.array import PiRGBArray
import paho.mqtt.client as mqtt
import os


def on_connect(client, userdata, flags, rc):
    print "Connected with result code %s" %(str(rc))
    messages.send_debug_message(client, module_name, "connected")


def on_message(client, userdata, msg):
    print("Received msg:" + str(msg.payload))
    try:
        jsonMsg = json.loads(msg.payload)
        cmdType = jsonMsg[cmd_type]
        
        print("Unknown command")
    except ValueError:
        print "ERROR: Unexpected values...."

module_name = os.path.basename(__file__)
camera_resolution_width  = config.get_config_value(config.CONFIG_RECORDING_RESOLUTION_WIDTH)
camera_resolution_height = config.get_config_value(config.CONFIG_RECORDING_RESOLUTION_HEIGHT)
camera_fps = config.get_config_value(config.CONFIG_RECORDING_FPS)

frames_topic = topics.VIDEO_STREAM_TOPIC

camera = PiCamera()
camera.resolution = (camera_resolution_width, camera_resolution_height)
camera.framerate = camera_fps
raw_frame = PiRGBArray(camera,size=(camera_resolution_width,camera_resolution_height))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start() 
frame_id = 0
for frame in camera.capture_continuous(raw_frame, format="rgb", use_video_port=True):
    frame_bytes = raw_frame.array.tobytes()
    print 'Publishing frame %d having size = %db' %(frame_id, len(frame_bytes))
       
    frame_metadata = {}
    frame_metadata['frame'] = {}
    frame_metadata['frame']['height'] = camera_resolution_height
    frame_metadata['frame']['width'] = camera_resolution_width
    frame_metadata['frame']['id'] = frame_id

    messages.publish_frame(client, frame_metadata, frame_bytes)
    raw_frame.truncate(0)
    frame_id += 1