'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

import json
import logging
import random
import sys
import time
import uuid

from datetime import datetime

try:
    import queue as Queue
except ImportError:
    import Queue as Queue 


try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic

try:
    from utils.aaslog import serviceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import serviceLogHandler,LogList

'''
    The skill generator extracts all the states from the transitions list.
    For each STATE, a seperate python class is created. This python class has two main
    functions run() and the next(). The run method is required to execute a set
    of instructions so that the class which represents a state could exhibit a specific behavior. 
    The next method defines the next class that has to be executed.
    
    Each transition is attributed by input document and outpput document.
    
    In the case of  input document, the class is expected to wait for the 
    arrival of a specific document type. While for the output document, the class
    is expected to send out the output document.
    
    This source-code consists of a base class and the all the classes each pertaining 
    to definite state of the skill state-machine. The base class represents the skill 
    and coordinates the transition from one state to another.
    
    The baseclass is responsible for collecting the documents from the external
    world (either from other skill that is part of the AAS or a skill part of 
    of another AAS). For this the baseclass maintains a queue one for each class. 
    
    The communication between any two skills of the same AAS or the skills of 
    different AAS is done in I4.0 language.
    
    An I4.0 message packet consists of a frame header and the interactionElements
    detail part. The frame element consists of Sender and Receiver elements. Under
    this the AASID's and respective skillnames can be specified.
    
    Also  every message packet is associated with a type, the type information is 
    specified in the Input and Output property tags under Transition collection in
    the AASx package.
    
    Based on the receive information in the frame header, the message is routed appropriate
    Skill. The base-class maintains a specific InboundQueue, into the messages dropped by the
    messagehandler. 
    
    A class specific inbound queue is defined in the baseclass for the classes defined in this
    source-code. A dictionary is also manitained, with key representing the messagetype and the
    value being the class specific inboundqueue.
    
    Every inbound message to the skill, is routed to the specific class based on its message type
    from the base CLaas.  
    
    For operational purposes, a dictionary variable is defined for each message type that this skill
    expects. 

    StateName_In         
    StateName_Queue 
        
    The sendMessage method in the baseclass submits an outbound message to the message handler so that
    it could be routed to its destination. Every class can access this method and publish the outbound
    messgae.  
    
    Accessing the asset entry within a specific class
        For accessing the asset, a developer has to write specific modules in the assetaccessadaptors
        package. In this version of LIAPAAS framework PLC OPCUA adaptor for reading and writing OPCUA
        variables is provided.
        
        The asset access information like IP address, port, username, password and the opcua variables
        are defined in the AASx configuration file.
        
        The module and the related OPCUA variable definitions with thin the skill.
        
        MODULE_NAME = "PLC_OPCUA"
        #Accessing the specifc assetaaccess adaptor 
        self.plcHandler = self.baseClass.pyAAS.assetaccessEndpointHandlers[MODULE_NAME] # 1
        
        #accessing the list property variables Dictionary are specified in the configuration file.  
        self.propertylist = self.plcHandler.propertylist # 2
        
        PLC_OPCUA represents the module specific to opcua adaptor to access the PLC
        
        The code snippets 1 and 2 need to be initialized in the constructor of the class        
        
    def StateName_Logic(self):
        self.plcHandler.read(self.propertylist["sPermission"])
        self.plcHandler.write(self.propertylist["sPermission"],"value")
        time.sleep(10)
      
       The propertylist is the dictionary, that has asset specific keys *OPCUA variables and the respective
        addresses.
    
    creating an outbound I40 message.
    
    Note : The communication between the skills that are part of the same AAS, or different
    AAS should happen within the I40 data format structure.
    
    A generic class is provided within the package utils.i40data (it is imported in the code).
    
    code snippet
    
    self.gen = Generic()
    self.frame = self.gen.createFrame(I40FrameData)
    
    
    If the receiver is a skill within the same AAS, the ReceiverAASID would be same as SenderAASID
    where the ReceiverRolename would be specific skill Name 
    
    The ReceiverAASID and ReceiverRolename could be obtained from sender part of the incoming message
    and these are to be provided empty, if there is no receiver.
    receiverId = self.baseClass.StateName_In["frame"]["sender"]["identification"]["id"]
    receiverRole = self.baseClass.StateName_In["frame"]["sender"]["role"]["name"]
    
    I40FrameData is a dictionary
    
    language : English, German
    format : Json, XML //self.baseClass.pyAAS.preferredCommunicationFormat
    reply-to : HTTP,MQTT,OPCUA (endpoint) // self.baseClass.pyAAS.preferedI40EndPoint
    serviceDesc : "short description of the message"

        {
        "type" : ,
        "messageId":messageId,
        "SenderAASID" : self.baseClass.AASID,
        "SenderRolename" : "BoringProvider",
        "conversationId" : "AASNetworkedBidding",
        "ReceiverAASID" :  receiverId,
        "ReceiverRolename" : receiverRole,
        "params" : {},
        "serviceDesc" : "",
        "language" : "",
        "format" : ""  
    } # In proposal needs to be confirmed
    
    the interactionElements part of the I40 frame usually contain the submodel elements,
    the respective the submodel element could be fetched from the submodel dictionary.
    
    The fetching of the submodel elements is done dynamically from the database.
    
    example Boring (should be same as the one specified in AASX file.)
    boringSubmodel = self.baseClass.pyAAS.dba.getSubmodelsbyId("BoringSubmodel")
    # result is list
    I40OutBoundMessage = {
                            "frame" : frame,
                            "interactionElements" : boringSubmodel
                        }
                        
    Saving the inbound and outbound messages into the datastore
    
    example :
    
    def retrieveMessage(self):
        self.baseClass.StateName_In = self.baseClass.StateName_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.StateName_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.baseClass.StateName_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
        
    
'''
    
class sendingProposal(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.waitingforServiceRequesterAnswer_Enabled = True
    

    def sendingProposal_Logic(self):
        pass # The developer has to write the logic that is required for the 
            # for the execution of the state
    
    def getPropertyElem(self,iSubmodel,propertyName):
        for submodelELem in iSubmodel["submodelElements"]:
            if submodelELem["idShort"] == "CommercialProperties":
                for sproperty in submodelELem["value"]:
                    if sproperty["idShort"] == propertyName:
                        return sproperty
             
             
    def addPropertyElems(self,oSubmodel,iSubmodel):
        i = 0
        listPrice = self.getPropertyElem(iSubmodel,"listprice")
        workStationLocation = self.getPropertyElem(iSubmodel,"workStationLocation")
        for submodelELem in oSubmodel["submodelElements"]:
            if submodelELem["idShort"] == "CommercialProperties":
                oSubmodel["submodelElements"][i]["value"].append(listPrice)
                oSubmodel["submodelElements"][i]["value"].append(workStationLocation) 
            i = i + 1
        return oSubmodel
            
    def create_Outbound_Message(self):
        self.oMessages = "proposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.WaitForCallForProposal_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["identification"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.baseClass.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.baseClass.pyAAS.dba.getMessageCount()["message"][0]+1),
                                    "SenderAASID" : self.baseClass.pyAAS.AASID,
                                    "SenderRolename" : self.baseClass.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            #oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            self.InElem = self.baseClass.pyAAS.dba.getSubmodelsbyId({"aasId":self.baseClass.pyAAS.AASID,"submodelId":"Boring"})["message"][0]
            boringSubmodel = self.addPropertyElems(message["interactionElements"][0],self.InElem)
            oMessage_Out ={"frame": self.frame,
                                    "interactionElements":[boringSubmodel]}
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: sendingProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendingProposal_Logic()
        
    def next(self):
        OutputDocument = "proposal"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.waitingforServiceRequesterAnswer_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = waitingforServiceRequesterAnswer(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitForCallForProposal(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.capabilitycheck_Enabled = True
    
    def retrieve_WaitForCallForProposal_Message(self):
        self.baseClass.WaitForCallForProposal_In = self.baseClass.WaitForCallForProposal_Queue.get()
        self.baseClass.subModelTypes = {}
        self.baseClass.proposalSubmodelTypes = {}
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.WaitForCallForProposal_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, 1):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            

    def WaitForCallForProposal_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: WaitForCallForProposal")
        # InputDocumentType"
        InputDocument = "callForProposal"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        self.baseClass.WaitForCallForProposal_In = {}
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.flush()
            while (((self.baseClass.WaitForCallForProposal_Queue).qsize()) == 0):
                time.sleep(1)
                #i = i + 1 
                #if i > 10: # Time to wait the next incoming message
                #    self.messageExist = False # If the waiting time expires, the loop is broken
                #    break
            if (self.messageExist):
                self.baseClass.WaitForCallForProposal_In = ""
                self.baseClass.proposalSubmodelTypes = {}
                self.baseClass.subModelTypes = {}
                self.baseClass.emptyAllQueues()                  
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitForCallForProposal_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitForCallForProposal_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.capabilitycheck_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = capabilitycheck(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class capabilitycheck(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingNotUnderstood_Enabled = True
        self.feasibilityCheck_Enabled = True
    
    def getProperty(self,submodelElem):
        if submodelElem["modelType"]["name"] == "Property":
            return submodelElem["value"] 
        elif submodelElem["modelType"]["name"] == "Range":
            return  {"min":submodelElem["min"],"max":submodelElem["max"]} 
    
    def getPropertyList(self,submodel):
        tempDict = {}
        for submodelElem in submodel["submodelElements"]:
            if submodelElem["idShort"] == "CommercialProperties":
                for elem in submodelElem["value"]:
                    tempDict[elem["idShort"]] = self.getProperty(elem)
                    
            elif submodelElem["idShort"] == "TechnicalProperties": 
                for elem in submodelElem["value"]:
                    if elem["idShort"] == "FunctionalProperties" or elem["idShort"] == "EnvironmentalProperties": 
                        for ele in elem["value"]:
                            tempDict[ele["idShort"]] = self.getProperty(ele)
                    elif elem["idShort"] == "WorkpieceProperties": 
                        for ele in elem["value"]:
                            if ele["idShort"] == "Dimensions":
                                for el in ele["value"]:
                                    tempDict[el["idShort"]] = self.getProperty(el)
                            else:
                                tempDict[ele["idShort"]] = self.getProperty(ele)      
        return tempDict                  
                    
    def capabilitycheck_Logic(self):
        # retrieving the submodel properties from the data base
        self.submodel = self.baseClass.pyAAS.dba.getAAsSubmodelsbyId(self.baseClass.pyAAS.AASID,"Boring")["message"][0]
        tempDict1 = self.getPropertyList(self.submodel)
        
        message = self.baseClass.WaitForCallForProposal_In
        self.iESubmodel = (message['interactionElements'][0])
        tempDict = self.getPropertyList(self.iESubmodel)

        try:
            if (tempDict["env"] != "live"):
                self.feasibilityCheck_Enabled = False
            else:       
                for key in list(tempDict1.keys()):
                    self.baseClass.subModelTypes[key] = tempDict1[key]        
                
                for key in list(tempDict.keys()):
                    self.baseClass.proposalSubmodelTypes[key] = tempDict[key]     
                    
                submodelTypeList = list(self.baseClass.subModelTypes.keys())
                if len(list(self.baseClass.proposalSubmodelTypes.keys())) == 0:
                    self.feasibilityCheck_Enabled = False
    
                for key in list(self.baseClass.proposalSubmodelTypes.keys()):
                    if (key in ["MaxDistanceToPreferredVenueOfProvision","PreferredVenueOfProvision","deliveryTime"]):
                        pass                
                    elif key not in submodelTypeList:
                        self.feasibilityCheck_Enabled = False
                        break
        except Exception as E:
            self.feasibilityCheck_Enabled = False
        
        if self.feasibilityCheck_Enabled:
            self.sendingNotUnderstood_Enabled = False
        else:
            self.feasibilityCheck_Enabled = False


    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: capabilitycheck")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.capabilitycheck_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingNotUnderstood_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendingNotUnderstood(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.feasibilityCheck_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = feasibilityCheck(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class waitingforServiceRequesterAnswer(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
        self.serviceProvision_Enabled = True
        self.plcHandler = self.baseClass.pyAAS.assetaccessEndpointHandlers["PLC_OPCUA"]
        self.propertylist = self.plcHandler.propertylist         
    
    def retrieve_waitingforServiceRequesterAnswer_Message(self):
        self.baseClass.waitingforServiceRequesterAnswer_In = self.baseClass.waitingforServiceRequesterAnswer_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.waitingforServiceRequesterAnswer_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.baseClass.waitingforServiceRequesterAnswer_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            

    def waitingforServiceRequesterAnswer_Logic(self):
        if (self.messageExist):
            if (self.baseClass.waitingforServiceRequesterAnswer_In["frame"]["type"] == "rejectProposal"):
                self.plcHandler.write(self.propertylist["sPermission"],"false")
                self.serviceProvision_Enabled = False
            else:
                self.WaitForCallForProposal_Enabled = False
        else:
            self.serviceProvision_Enabled = False

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: waitingforServiceRequesterAnswer")
        # InputDocumentType"
        InputDocument = "acceptProposal / rejectProposal"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        self.plcHandler.write(self.propertylist["sPermission"],"true")
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            #sys.stdout.write(" Waiting for response")
            #sys.stdout.flush()
            while (((self.baseClass.waitingforServiceRequesterAnswer_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 60: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_waitingforServiceRequesterAnswer_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.waitingforServiceRequesterAnswer_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.WaitForCallForProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.serviceProvision_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = serviceProvision(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class checkingSchedule(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingRefuse_Enabled = True
        self.PriceCalculation_Enabled = True
        self.plcHandler = self.baseClass.pyAAS.assetaccessEndpointHandlers["PLC_OPCUA"]
        self.propertylist = self.plcHandler.propertylist       

    def checkingSchedule_Logic(self):
        try:
            sPermissionVariable = self.plcHandler.read(self.propertylist["sPermission"])  
            if sPermissionVariable == "Error":
                self.PriceCalculation_Enabled = False
            else:
                self.sendingRefuse_Enabled = False
        except Exception as E:
            self.PriceCalculation_Enabled = False

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: checkingSchedule")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.checkingSchedule_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingRefuse_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendingRefuse(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.PriceCalculation_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = PriceCalculation(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class PriceCalculation(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingProposal_Enabled = True
    

    def PriceCalculation_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: PriceCalculation")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.PriceCalculation_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendingProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendingRefuse(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
    

    def sendingRefuse_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "refuseProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.WaitForCallForProposal_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["identification"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.baseClass.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.baseClass.pyAAS.dba.getMessageCount()["message"][0]+1),
                                    "SenderAASID" : self.baseClass.pyAAS.AASID,
                                    "SenderRolename" : self.baseClass.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame,"interactionElements":[]}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #self.InElem = self.baseClass.pyAAS.dba.getSubmodelsbyId({"aasId":self.baseClass.pyAAS.AASID,"submodelId":"BoringSubmodel"})
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":self.InElem["message"]}
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: sendingRefuse")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendingRefuse_Logic()
        
    def next(self):
        OutputDocument = "refuseProposal"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitForCallForProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendinPropoposalporvisionConfirm(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
    

    def sendinPropoposalporvisionConfirm_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "informConfirm".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.waitingforServiceRequesterAnswer_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["identification"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.baseClass.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.baseClass.pyAAS.dba.getMessageCount()["message"][0]+1),
                                    "SenderAASID" : self.baseClass.pyAAS.AASID,
                                    "SenderRolename" : self.baseClass.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #self.InElem = self.baseClass.pyAAS.dba.getSubmodelsbyId({"aasId":self.baseClass.pyAAS.AASID,"submodelId":"BoringSubmodel"})
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":self.InElem["message"]}
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: sendinPropoposalporvisionConfirm")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendinPropoposalporvisionConfirm_Logic()
        
    def next(self):
        OutputDocument = "informConfirm"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitForCallForProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class serviceProvision(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendinPropoposalporvisionConfirm_Enabled = True
        self.WaitForCallForProposal_Enabled = True
        self.plcHandler = self.baseClass.pyAAS.assetaccessEndpointHandlers["PLC_OPCUA"]
        self.propertylist = self.plcHandler.propertylist       

    def serviceProvision_Logic(self):
        plcBoool = True
        while (plcBoool):
            #sPermissionVariable = "FALSE"
            #time.sleep(5)
            sPermissionVariable = self.plcHandler.read(self.propertylist["sPermission"])
            if  (sPermissionVariable.upper() == "FALSE"):
                plcBoool = False
        
        self.WaitForCallForProposal_Enabled = False

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: serviceProvision")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.serviceProvision_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendinPropoposalporvisionConfirm_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendinPropoposalporvisionConfirm(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.WaitForCallForProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendingNotUnderstood(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
    

    def sendingNotUnderstood_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "notUnderstood".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.WaitForCallForProposal_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["identification"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.baseClass.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.baseClass.pyAAS.dba.getMessageCount()["message"][0]+1),
                                    "SenderAASID" : self.baseClass.pyAAS.AASID,
                                    "SenderRolename" : self.baseClass.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame,"interactionElements":[]}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #self.InElem = self.baseClass.pyAAS.dba.getSubmodelsbyId({"aasId":self.baseClass.pyAAS.AASID,"submodelId":"BoringSubmodel"})
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":self.InElem["message"]}
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: sendingNotUnderstood")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendingNotUnderstood_Logic()
        
    def next(self):
        OutputDocument = "notUnderstood"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitForCallForProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class feasibilityCheck(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingRefuse_Enabled = True
        self.checkingSchedule_Enabled = True
    

    def feasibilityCheck_Logic(self):
        self.itemsCheck = {"MaterialOfWorkpiece":"Property","Height":"Range",
         "Depth":"Range","Width":"Range","ReferencedStandartOfMaterialShortName":"Property",
         "TensileStrengthOfMaterial":"Range","WeightOfWorkpiece":"Range","Hardness":"TRange",
         "drillingDiameter":"Range","drillingDepth":"Range",
         "RoughnessAverageOfBore":"Range","ISOToleranceClass":"Range"}
        
        feasibilityLen = 0
        for key in list(self.itemsCheck):
            item = self.itemsCheck[key]
            if  item == "Property":
                if (key == "MaterialOfWorkpiece"):
                    feasibilityLen = feasibilityLen + 1 
                elif ( self.baseClass.proposalSubmodelTypes[key] == self.baseClass.subModelTypes[key] ):
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,self.baseClass.proposalSubmodelTypes[key],self.baseClass.subModelTypes[key])
            elif item == "Range":
                value = self.baseClass.proposalSubmodelTypes[key]
                min = float(self.baseClass.subModelTypes[key]["min"])
                max = float(self.baseClass.subModelTypes[key]["max"])
                if float(value) >= min and float(value) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,value,self.baseClass.subModelTypes[key])                    
            elif item == "TRange":
                value = self.baseClass.proposalSubmodelTypes[key]
                min = float((self.baseClass.subModelTypes[key]["min"]).split(" ")[1])
                max = float((self.baseClass.subModelTypes[key]["max"]).split(" ")[1])
                tempValue = value.split(" ")[1]
                if float(tempValue) >= min and float(tempValue) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,value,self.baseClass.subModelTypes[key])                    
                    
        if feasibilityLen == 12:
            self.sendingRefuse_Enabled = False
        else:
            self.checkingSchedule_Enabled = False

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: feasibilityCheck")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.feasibilityCheck_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingRefuse_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendingRefuse(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.checkingSchedule_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = checkingSchedule(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        



class BoringProvider(object):
    '''
    classdocs
    '''

        
    def initstateSpecificQueueInternal(self):
        
        self.QueueDict = {}
        
        self.sendingProposal_Queue = Queue.Queue()
        self.WaitForCallForProposal_Queue = Queue.Queue()
        self.capabilitycheck_Queue = Queue.Queue()
        self.waitingforServiceRequesterAnswer_Queue = Queue.Queue()
        self.checkingSchedule_Queue = Queue.Queue()
        self.PriceCalculation_Queue = Queue.Queue()
        self.sendingRefuse_Queue = Queue.Queue()
        self.sendinPropoposalporvisionConfirm_Queue = Queue.Queue()
        self.serviceProvision_Queue = Queue.Queue()
        self.sendingNotUnderstood_Queue = Queue.Queue()
        self.feasibilityCheck_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "callForProposal": self.WaitForCallForProposal_Queue,
              "rejectProposal": self.waitingforServiceRequesterAnswer_Queue,
              "acceptProposal": self.waitingforServiceRequesterAnswer_Queue,
            }
    
    def initInBoundMessages(self):
            self.WaitForCallForProposal_In = {}
            self.waitingforServiceRequesterAnswer_In = {}
    
    def createStatusMessage(self):
        self.StatusDataFrame =      {
                                "semanticProtocol": self.semanticProtocol,
                                "type" : "StausChange",
                                "messageId" : "StausChange_1",
                                "SenderAASID" : self.pyAAS.AASID,
                                "SenderRolename" : self.skillName,
                                "conversationId" : "AASNetworkedBidding",
                                "ReceiverAASID" :  self.pyAAS.AASID + "/"+self.skillName,
                                "ReceiverRolename" : "SkillStatusChange"
                            }
        self.statusframe = self.gen.createFrame(self.StatusDataFrame)
        self.statusInElem = self.getStatusResponseSubmodel()
        self.statusMessage ={"frame": self.statusframe,
                                "interactionElements":self.statusInElem["message"]}
 
    
    def __init__(self, pyAAS):
        '''
        Constructor
        '''
        
        self.SKILL_STATES = {
                          "sendingProposal": "sendingProposal",  "WaitForCallForProposal": "WaitForCallForProposal",  "capabilitycheck": "capabilitycheck",  "waitingforServiceRequesterAnswer": "waitingforServiceRequesterAnswer",  "checkingSchedule": "checkingSchedule",  "PriceCalculation": "PriceCalculation",  "sendingRefuse": "sendingRefuse",  "sendinPropoposalporvisionConfirm": "sendinPropoposalporvisionConfirm",  "serviceProvision": "serviceProvision",  "sendingNotUnderstood": "sendingNotUnderstood",  "feasibilityCheck": "feasibilityCheck",
                       }
        
        self.pyAAS = pyAAS
        self.skillName = "BoringProvider"
        self.initstateSpecificQueueInternal()
        self.initInBoundMessages()
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = self.enabledStatus["Y"]
        
        self.semanticProtocol = "http://www.vdi.de/gma720/vdi2193_2/bidding"

        self.skillLogger = logging.getLogger(str(self.__class__.__name__) + ' Service Instance' )
        self.skillLogger.setLevel(logging.DEBUG)
        self.gen = Generic()
        self.createStatusMessage()
        self.productionStepSeq = []
        self.responseMessage = {}
        self.subModelTypes = {}
        self.proposalSubmodelTypes = {}
    
    def emptyAllQueues(self):
        waitingforServiceRequesterAnswerList = list(self.waitingforServiceRequesterAnswer_Queue.queue)
        for elem in range(0,len(waitingforServiceRequesterAnswerList)):
            self.waitingforServiceRequesterAnswer_Queue.get()
                
    def Start(self, msgHandler,skillDetails,aasIndex):
        self.msgHandler = msgHandler
        self.skillDetails = skillDetails
        self.aasIndex = aasIndex
        
        
        self.commandLogger_handler = logging.StreamHandler(stream=sys.stdout)
        self.commandLogger_handler.setLevel(logging.DEBUG)
        
        self.fileLogger_Handler = logging.FileHandler(self.pyAAS.base_dir+"/logs/"+self.skillName+".LOG")
        self.fileLogger_Handler.setLevel(logging.DEBUG)
        
        self.listHandler = serviceLogHandler(self.msgHandler.BoringProviderLogList)
        self.listHandler.setLevel(logging.DEBUG)
        
        self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        
        self.listHandler.setFormatter(self.Handler_format)
        self.commandLogger_handler.setFormatter(self.Handler_format)
        self.fileLogger_Handler.setFormatter(self.Handler_format)
        
        self.skillLogger.addHandler(self.listHandler)
        self.skillLogger.addHandler(self.commandLogger_handler)
        self.skillLogger.addHandler(self.fileLogger_Handler)

        WaitForCallForProposal_1 = WaitForCallForProposal(self)
        self.stateChange("WaitForCallForProposal")
        currentState = WaitForCallForProposal_1
        self.enabledState = self.skillDetails["enabled"]
        
        
        while (True):
            if ((currentState.__class__.__name__) == "WaitForCallForProposal"):
                if(self.enabledState):
                    self.currentConversationId = "temp"
                    currentState.run()
                    ts = currentState.next()
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
            else:
                currentState.run()
                ts = currentState.next()
                if not (ts):
                    break
                else:
                    if ((ts.__class__.__name__) == "WaitForCallForProposal"):
                        self.currentConversationId = "temp"
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
    
    def geCurrentSKILLState(self):
        return self.SKILL_STATE
    
    def getListofSKILLStates(self):
        return self.SKILL_STATES
    
    
    def stateChange(self, STATE):
        pass#self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        #self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        #self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        #self.sendMessage(self.statusMessage)
    
    def sendMessage(self, sendMessage):
        self.msgHandler.putObMessage(sendMessage)
    
    def receiveMessage(self,inMessage):
        try:    
            _conversationId = str(inMessage['frame']['conversationId'])
            senderRole = str(inMessage["frame"]['sender']['role']["name"])
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass #self.skillLogger.info("Raise an Exception " + str(E))



if __name__ == '__main__':
    
    lm2 = BoringProvider()
    lm2.Start('msgHandler')