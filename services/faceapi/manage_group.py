'''
This script creates a group in Azure FaceAPI 
Cmd line parameters:
command - required
groupId - required
groupDescription - optional
'''
import sys
import json
import cognitive_face as CF
import paho.mqtt.client as mqtt

# Config
faceApiEndpoint = "https://westus.api.cognitive.microsoft.com/face/v1.0/"
faceApiKey = "0118754ef3d3423a91a28c21fab6e342"
CF.Key.set(faceApiKey)
CF.BaseUrl.set(faceApiEndpoint)

mqttBroker = "172.24.10.92"
mqttPort = 1883
mqttTopicBase = "group_manager"
# Config

# MQTT functions

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mqttTopicBase)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("mqtt msg: "+msg.topic+" "+str(msg.payload))
    message = json.loads(msg.payload)
    command = tryGetParameter(message, 'cmd')
    groupId = tryGetParameter(message, "groupId")
    description = tryGetParameter(message, "description")

    if command == None or groupId == None:
        print("cmd and groupId are required")
    else:
        executeCommand(command, groupId, description)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttBroker, mqttPort, 60)

# MQTT functions END

# Group manager functions
def createGroup(groupId, displayName, userData): 
    try:
        res = CF.person_group.create(groupId, displayName, userData)
        print(res)
        return True
    except CF.util.CognitiveFaceException as e:
        print(e)
        return False

def deleteGroup(groupId):
    try:
        CF.person_group.delete(groupId)
        return True
    except Exception as e:
        print(e)
        return False

# Group manager functions END

# Util functions

def tryGetParameter(myList, idx):
    try:
        return myList[idx]
    except Exception:
        return None

# Util functions END

def runGroupManager():
    print("runnning")
    client.loop_forever()

def executeCommand(command, groupId, description):
    if command == "c":
        if createGroup(groupId, groupId, description):
            print("Group {} created".format(groupId))
        else:
            print("Could not create group {}".format(groupId))
    elif command == "d":
        if deleteGroup(groupId):
            print("Group {} deleted".format(groupId))
        else:
            print("Failed to delete group {}".format(groupId))
        

if __name__ == '__main__':
    if len(sys.argv) == 1:
        #if no args run continuously
        runGroupManager()

    #else use args to execute command
    if len(sys.argv) > 2:
        command = tryGetParameter(sys.argv,1)
        groupId = tryGetParameter(sys.argv,2)
        description = tryGetParameter(sys.argv,3)
           
        executeCommand(command, groupId, description)
            
            
        
    else:
        print("Group name and command are required")
