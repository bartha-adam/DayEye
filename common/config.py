import ruamel.yaml as yaml
import os

CONFIG_DELIMITER  = "/"

CONFIG_SECTION_COMMON = "common"

CONFIG_SECTION_RECORDING = "recording"
CONFIG_RECORDING_RESOLUTION = CONFIG_SECTION_RECORDING + CONFIG_DELIMITER + "resolution"
CONFIG_RECORDING_RESOLUTION_WIDTH = CONFIG_RECORDING_RESOLUTION + CONFIG_DELIMITER + "width"
CONFIG_RECORDING_RESOLUTION_HEIGHT = CONFIG_RECORDING_RESOLUTION + CONFIG_DELIMITER + "height"
CONFIG_RECORDING_FPS = CONFIG_SECTION_RECORDING + CONFIG_DELIMITER + "fps"

CONFIG_SECTION_FACEAPI = "faceapi"
CONFIG_FACEAPI_BASEURL = CONFIG_SECTION_FACEAPI + CONFIG_DELIMITER + "baseurl"
CONFIG_FACEAPI_KEY = CONFIG_SECTION_FACEAPI + CONFIG_DELIMITER + "key"
CONFIG_FACEAPI_IDENTITY_CONFIDENCE_THRESHOLD = CONFIG_SECTION_FACEAPI + CONFIG_DELIMITER + "identity_confidence_threshold"
CONFIG_FACEAPI_GROUP_NAME = CONFIG_SECTION_FACEAPI + CONFIG_DELIMITER + "group_name"

CONFIG_SECTION_MQTT = "mqtt"
CONFIG_MQTT_BROKER = CONFIG_SECTION_MQTT+CONFIG_DELIMITER+"broker"
CONFIG_MQTT_PORT = CONFIG_SECTION_MQTT+CONFIG_DELIMITER+"port"

stored_config = None

def get_config():
    global stored_config
    if stored_config == None:
        folder = "./"
        config_file_name = "config.yaml"
        config_file = None
        while os.path.exists(folder):
            if os.path.isfile(folder + config_file_name):
                config_file = folder + config_file_name
                print("Found config file at %s" % (config_file))
                break
            folder = "../" + folder
        if config_file == None:
            raise Exception("Config file not found!") 

        with open(config_file, 'r') as stream:
            try:
                stored_config = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)
    return stored_config

def get_config_value(path):
    print('Loading config from %s' %(path))
    config = get_config() # root section
    sections = path.split(CONFIG_DELIMITER) 
    for section in sections:
        config = config[section]
        if config == None:
            raise Exception("Config path not found %s" % (path)) 
    print('  %s => %s' %(path, config))
    return config



