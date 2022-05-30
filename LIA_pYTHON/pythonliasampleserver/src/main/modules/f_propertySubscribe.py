'''
Created on 24 Oct 2021

@author: pakala
'''
try:
    from utils.utils import ExecuteDBModifier
except ImportError:
    from main.utils.utils import ExecuteDBModifier
    
from datetime import datetime
import random

def createNewQualifier(newValue):
    return {
              "type": "value",
              "valueType": "",
              "value": newValue,
              "modelType": {
                "name": "Qualifier"
              }
            }

def createRandomData(propertyName):
    peak_chance = random.randint(0, 100)
    
    if peak_chance < 10:  # 10% chance for under-value
        if (propertyName == "Processvalue"):
            return float(random.randint(2309, 2409) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(6889, 6989) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)
    elif peak_chance > 90:  # 10% chance for peak-value
        if (propertyName == "Processvalue"):
            return float(random.randint(2415, 2515) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(7045, 7145) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)
    else:
        if (propertyName == "Processvalue"):
            return float(random.randint(2409, 2415) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(6989, 7045) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)


class AssetOPCUAEndPointSubscription(object):
 
    def __init__(self,pyAAS,params):
        self.pyAAS = pyAAS
        self.params = params
        
    def datachange_notification(self, node, val, data):
        self.valueList = self.params['value']
        self.labelList = self.params['label']
        
        del self.valueList[0]
        del self.labelList[0]
        self.labelList.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.valueList.append(val)
        self.pyAAS.tdPropertiesList[self.params["key"]]["value"] = self.valueList
        self.pyAAS.tdPropertiesList[self.params["key"]]["label"] = self.labelList
 
    def event_notification(self, event):
        print(event)


def function(pyAAS, *args):
    params = args[0]
    accessURI = params["href"]
    if (accessURI[0:8] == "opc.tcp:"):
        endPointSUbHandler = AssetOPCUAEndPointSubscription(pyAAS,params)
        pyAAS.assetaccessEndpointHandlers["OPCUA"].subscribe(accessURI,endPointSUbHandler)
    
        #edm = ExecuteDBModifier(pyAAS)
        #dataBaseResponse = edm.executeModifer({"data":{"updateData":createNewQualifier(newValue),"aasId":params["aasId"],"submodelId":submodelName,"aasId":pyAAS.AASID,"idShortPath":idShortPath},"method":"putSubmodelElementQualbyId","instanceId" : str(uuid.uuid1())})
    '''
                
    '''    