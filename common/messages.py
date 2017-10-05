import json
import binascii

from struct import *
from common import config
from common import topics

cmd_type = "cmd"
cmd_debug = "debug"
cmd_debug_module = "module"
cmd_debug_msg = "msg"

debug_topic = topics.DEBUG_TOPIC
video_stream_topic = topics.VIDEO_STREAM_TOPIC

def send_debug_message(client, module_name, message):
    data = {}
    data[cmd_type] = cmd_debug
    data[cmd_debug_module] = module_name
    data[cmd_debug_msg] = message
    json_data = json.dumps(data)
    client.publish(debug_topic, json_data)

def publish_frame(client, frame_metadata_json, raw_frame):
    package = compose_frame(frame_metadata_json, raw_frame)
    client.publish(video_stream_topic, package)

def compose_frame(frame_metadata_json, raw_frame):
    frame_metadata_str = json.dumps(frame_metadata_json)
    frame_bin_offset = len(frame_metadata_str)
    package_bin_header = pack('h', frame_bin_offset)
    package = package_bin_header + frame_metadata_str + raw_frame
    # print "Pacakge len =%d" %(len(package))
    # print "Package hash %s" %(hash(package))
    # print "Package header len = %d" %(len(package_bin_header))
    # print "Frame start 0x%s" % (binascii.b2a_hex(bytearray(raw_frame[0:100])))
    # print "Frame end   0x%s" % (binascii.b2a_hex(bytearray(raw_frame[-100:])))
    return package

def parse_frame(raw_message):
    package_bin_header = raw_message[:2]
    frame_bin_offset = 2 + unpack('h', package_bin_header)[0]
    frame_metadata_str = raw_message[2: frame_bin_offset]
    frame_metadata_json = json.loads(frame_metadata_str)
    raw_frame = raw_message[frame_bin_offset:]

    # print "Package len %s" %(len(raw_message))
    # print "Package hash %s" %(hash(raw_message))
    # print "Package header len = %d" %(len(package_bin_header))
    # print "Frame offset %d" % (frame_bin_offset)
    # print "Frame data length %d" % (len(raw_frame))
    # print "Frame start 0x%s" % (binascii.b2a_hex(bytearray(raw_frame[0:100])))
    # print "Frame end   0x%s" % (binascii.b2a_hex(bytearray(raw_frame[-100:])))
    return (frame_metadata_json, raw_frame)

