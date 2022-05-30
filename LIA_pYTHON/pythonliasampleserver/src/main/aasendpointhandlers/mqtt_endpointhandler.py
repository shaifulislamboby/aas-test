'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

import json
import os
import threading
import uuid

try:
    from abstract.endpointhandler import AASEndPointHandler
except ImportError:
    from main.abstract.endpointhandler import AASEndPointHandler

import paho.mqtt.client as mqtt

class AASEndPointHandler(AASEndPointHandler):
    
    def __init__(self, pyAAS, msgHandler):
        self.pyAAS = pyAAS
        self.topicname = pyAAS.AASID
        self.msgHandler = msgHandler
    
    def on_connect(self, client, userdata, flags, rc):
        self.pyAAS.serviceLogger.info("MQTT channels are succesfully connected.")
        
    def configure(self):
        self.ipaddressComdrv = self.pyAAS.lia_env_variable["LIA_AAS_MQTT_HOST"]
        self.portComdrv = int(self.pyAAS.lia_env_variable["LIA_AAS_MQTT_PORT"])
        
        self.client = mqtt.Client(client_id=str(uuid.uuid4()))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.retrieveMessage
        
    def update(self):
        try:
            self.stop()
            self.client.connect(self.ipaddressComdrv, port=(self.portComdrv))
            topicsList = []
            for _ids in list(self.pyAAS.aasIdentificationIdList.keys()):
                topicsList.append((_ids,0))
            self.client.subscribe(topicsList)
            self.client.loop_forever()
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error with the MQTT Subscription"+ str(E))
    
    def restart(self):
        try :
            mqttClientThread1 = threading.Thread(target=self.update)
            mqttClientThread1.start()
          
        except Exception as e:
            self.pyAAS.serviceLogger.info('Unable to connect to the mqtt server ' + str(e))
            os._exit(0)
        self.pyAAS.serviceLogger.info("MQTT channels are started")
    
    def start(self):
        try :
            mqttClientThread1 = threading.Thread(target=self.update)
            mqttClientThread1.start()
          
        except Exception as e:
            self.pyAAS.serviceLogger.info('Unable to connect to the mqtt server ' + str(e))
            os._exit(0)
        self.pyAAS.serviceLogger.info("MQTT channels are started")
            

    def stop(self):
        try: 
            self.client.loop_stop(force=False)
            self.client.disconnect()
            
        except Exception as e:
            self.pyAAS.serviceLogger.info('Error disconnecting to the server ' + str(e))

    def dispatchMessage(self, send_Message): 
        publishTopic = self.pyAAS.BroadCastMQTTTopic
        try:
            publishTopic = send_Message["frame"]["receiver"]["identification"]["id"]
        except:
            pass
        try:
            if (publishTopic in list(self.pyAAS.aasIdentificationIdList.keys())):
                self.msgHandler.putIbMessage(send_Message)
            else:
                self.client.publish("AASpillarbox", str(json.dumps(send_Message)))
        except Exception as e:
            self.pyAAS.serviceLogger.info("Unable to publish the message to the mqtt server", str(e))
            
    def retrieveMessage(self, client, userdata, msg):
        try:
            msg1 = str(msg.payload, "utf-8")
            jsonMessage = json.loads(msg1)             
            if (jsonMessage["frame"]["sender"]["identification"]["id"] == self.pyAAS.AASID):
                self.msgHandler.putIbMessage(jsonMessage)
            else:
                self.msgHandler.putIbMessage(jsonMessage)
        except:
            pass
            
