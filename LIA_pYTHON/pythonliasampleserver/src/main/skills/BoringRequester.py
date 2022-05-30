'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import logging
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
        "SenderRolename" : "BoringRequester",
        "conversationId" : "AASNetworkedBidding",
        "replyBy" :  "",   # "The communication protocol that the AAS needs to use while sending message to other AAS."
        "replyTo" : "",    # "The communication protocol that the receipient AAS should use for reply"   
                           # In case the message needs to be routed to another skill please "Internal"
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
    
class WaitForSPProposal(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.noProposalReceived_Enabled = True
        self.EvaluateProposal_Enabled = True
    
    def retrieve_WaitForSPProposal_Message(self):
        self.baseClass.WaitForSPProposal_In = self.baseClass.WaitForSPProposal_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.WaitForSPProposal_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.baseClass.WaitForSPProposal_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            

    def WaitForSPProposal_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: WaitForSPProposal")
        # InputDocumentType"
        InputDocument = "proposal"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.baseClass.WaitForSPProposal_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 10: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitForSPProposal_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitForSPProposal_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.noProposalReceived_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = noProposalReceived(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.EvaluateProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = EvaluateProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class cfpConfiguration(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.SendCFP_Enabled = True
    

    def cfpConfiguration_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: cfpConfiguration")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.cfpConfiguration_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.SendCFP_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = SendCFP(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendCompletionResponse(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforNewOrder_Enabled = True
    

    def sendCompletionResponse_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "OrderStatus".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.StateName_In
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
                                    "replyBy" :  self.baseClass.pyAAS.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
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
        self.baseClass.skillLogger.info("StartState: sendCompletionResponse")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendCompletionResponse_Logic()
        
    def next(self):
        OutputDocument = "OrderStatus"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitforNewOrder_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitforNewOrder(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendTransportOrder(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforTransportOrderCompletion_Enabled = True
    

    def sendTransportOrder_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "Order".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.StateName_In
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
                                    "replyBy" :  self.baseClass.pyAAS.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
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
        self.baseClass.skillLogger.info("StartState: sendTransportOrder")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendTransportOrder_Logic()
        
    def next(self):
        OutputDocument = "Order"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitforTransportOrderCompletion_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitforTransportOrderCompletion(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendacceptProposal(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforInformConfirm_Enabled = True
    

    def sendacceptProposal_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "acceptProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.StateName_In
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
                                    "replyBy" :  self.baseClass.pyAAS.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
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
        self.baseClass.skillLogger.info("StartState: sendacceptProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendacceptProposal_Logic()
        
    def next(self):
        OutputDocument = "acceptProposal"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitforInformConfirm_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitforInformConfirm(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitforInformConfirm(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
    
    def retrieve_WaitforInformConfirm_Message(self):
        self.baseClass.WaitforInformConfirm_In = self.baseClass.WaitforInformConfirm_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.WaitforInformConfirm_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.baseClass.WaitforInformConfirm_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            

    def WaitforInformConfirm_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: WaitforInformConfirm")
        # InputDocumentType"
        InputDocument = "informConfirm"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.baseClass.WaitforInformConfirm_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 10: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforInformConfirm_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitforInformConfirm_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class noProposalReceived(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
    

    def noProposalReceived_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: noProposalReceived")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.noProposalReceived_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitforNewOrder(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.cfpConfiguration_Enabled = True
    
    def retrieve_WaitforNewOrder_Message(self):
        self.baseClass.WaitforNewOrder_In = self.baseClass.WaitforNewOrder_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.WaitforNewOrder_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.baseClass.WaitforNewOrder_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            

    def WaitforNewOrder_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: WaitforNewOrder")
        # InputDocumentType"
        InputDocument = "Order"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.baseClass.WaitforNewOrder_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                #if i > 10: # Time to wait the next incoming message
                #    self.messageExist = False # If the waiting time expires, the loop is broken
                #    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforNewOrder_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitforNewOrder_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.cfpConfiguration_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = cfpConfiguration(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class sendrejectProposal(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
        self.sendTransportOrder_Enabled = True
    

    def sendrejectProposal_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "rejectProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.StateName_In
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
                                    "replyBy" :  self.baseClass.pyAAS.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
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
        self.baseClass.skillLogger.info("StartState: sendrejectProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendrejectProposal_Logic()
        
    def next(self):
        OutputDocument = "rejectProposal"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.sendCompletionResponse_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.sendTransportOrder_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendTransportOrder(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class SendCFP(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForSPProposal_Enabled = True
    

    def SendCFP_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    def create_Outbound_Message(self):
        self.oMessages = "callForProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.baseClass.StateName_In
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
                                    "replyBy" :  self.baseClass.pyAAS.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
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
        self.baseClass.skillLogger.info("StartState: SendCFP")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.SendCFP_Logic()
        
    def next(self):
        OutputDocument = "callForProposal"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.baseClass.sendMessage(outbMessage)
        
        if (self.WaitForSPProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = WaitForSPProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class EvaluateProposal(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendrejectProposal_Enabled = True
    

    def EvaluateProposal_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: EvaluateProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        self.EvaluateProposal_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendrejectProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendrejectProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitforTransportOrderCompletion(object):
    
    def __init__(self, baseClass):
        '''
        '''
        self.baseClass = baseClass
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendacceptProposal_Enabled = True
        self.sendCompletionResponse_Enabled = True
    
    def retrieve_WaitforTransportOrderCompletion_Message(self):
        self.baseClass.WaitforTransportOrderCompletion_In = self.baseClass.WaitforTransportOrderCompletion_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.baseClass.WaitforTransportOrderCompletion_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.baseClass.WaitforTransportOrderCompletion_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.baseClass.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "message":message})
            

    def WaitforTransportOrderCompletion_Logic(self):
        pass # The developer has to write the logic that is required for the 
             # for the execution of the state

    
    def run(self):
            
        self.baseClass.skillLogger.info("\n #############################################################################")
        # StartState
        self.baseClass.skillLogger.info("StartState: WaitforTransportOrderCompletion")
        # InputDocumentType"
        InputDocument = "OrderStatus"
        self.baseClass.skillLogger.info("InputDocument : " + InputDocument)
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.baseClass.WaitforTransportOrderCompletion_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 10: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforTransportOrderCompletion_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitforTransportOrderCompletion_Logic()
        
    def next(self):
        OutputDocument = "NA"
        self.baseClass.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendacceptProposal_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendacceptProposal(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        if (self.sendCompletionResponse_Enabled):
            self.baseClass.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.baseClass)
            self.baseClass.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.baseClass.skillLogger.info("############################################################################# \n")
            return ts
        



class BoringRequester(object):
    '''
    classdocs
    '''

        
    def initstateSpecificQueueInternal(self):
        
        self.QueueDict = {}
        
        self.WaitForSPProposal_Queue = Queue.Queue()
        self.cfpConfiguration_Queue = Queue.Queue()
        self.sendCompletionResponse_Queue = Queue.Queue()
        self.sendTransportOrder_Queue = Queue.Queue()
        self.sendacceptProposal_Queue = Queue.Queue()
        self.WaitforInformConfirm_Queue = Queue.Queue()
        self.noProposalReceived_Queue = Queue.Queue()
        self.WaitforNewOrder_Queue = Queue.Queue()
        self.sendrejectProposal_Queue = Queue.Queue()
        self.SendCFP_Queue = Queue.Queue()
        self.EvaluateProposal_Queue = Queue.Queue()
        self.WaitforTransportOrderCompletion_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "proposal": self.WaitForSPProposal_Queue,
              "informConfirm": self.WaitforInformConfirm_Queue,
              "Order": self.WaitforNewOrder_Queue,
              "OrderStatus": self.WaitforTransportOrderCompletion_Queue,
            }
    
    def initInBoundMessages(self):
            self.WaitforInformConfirm_In = {}
            self.WaitforTransportOrderCompletion_In = {}
            self.WaitforNewOrder_In = {}
            self.WaitForSPProposal_In = {}
    
    def createStatusMessage(self):
        self.StatusDataFrame =      {
                                "semanticProtocol": self.semanticProtocol,
                                "type" : "StausChange",
                                "messageId" : "StausChange_1",
                                "SenderAASID" : self.pyAAS.AASID,
                                "SenderRolename" : self.skillName,
                                "conversationId" : "AASNetworkedBidding",
                                "replyBy" :  "",
                                "replyTo" :"",
                                "ReceiverAASID" :  self.pyAAS.AASID + "/"+self.skillName,
                                "ReceiverRolename" : "SkillStatusChange"
                            }
        self.statusframe = self.gen.createFrame(self.StatusDataFrame)
        self.statusInElem = self.pyAAS.aasConfigurer.getStatusResponseSubmodel()
        self.statusMessage ={"frame": self.statusframe,
                                "interactionElements":[self.statusInElem]}    
 
    
    def __init__(self, pyAAS):
        '''
        Constructor
        '''
        
        self.SKILL_STATES = {
                          "WaitForSPProposal": "WaitForSPProposal",  "cfpConfiguration": "cfpConfiguration",  "sendCompletionResponse": "sendCompletionResponse",  "sendTransportOrder": "sendTransportOrder",  "sendacceptProposal": "sendacceptProposal",  "WaitforInformConfirm": "WaitforInformConfirm",  "noProposalReceived": "noProposalReceived",  "WaitforNewOrder": "WaitforNewOrder",  "sendrejectProposal": "sendrejectProposal",  "SendCFP": "SendCFP",  "EvaluateProposal": "EvaluateProposal",  "WaitforTransportOrderCompletion": "WaitforTransportOrderCompletion",
                       }
        
        self.pyAAS = pyAAS
        self.skillName = "BoringRequester"
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
        
    def Start(self, msgHandler,skillDetails,aasIndex):
        self.msgHandler = msgHandler
        self.skillDetails = skillDetails
        self.aasIndex = aasIndex
        
        self.commandLogger_handler = logging.StreamHandler(stream=sys.stdout)
        self.commandLogger_handler.setLevel(logging.DEBUG)
        
        self.skillLogger = logging.getLogger(str(self.__class__.__name__) + "_"+ "_" + str(self.aasIndex))
        self.fileLogger_Handler.setLevel(logging.DEBUG)
        
        self.listHandler = serviceLogHandler(self.pyAAS.skilllogListDict[self.aasIndex][self.skillName])
        self.listHandler.setLevel(logging.DEBUG)
        
        self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        
        self.listHandler.setFormatter(self.Handler_format)
        self.commandLogger_handler.setFormatter(self.Handler_format)
        self.fileLogger_Handler.setFormatter(self.Handler_format)
        
        self.skillLogger.addHandler(self.listHandler)
        self.skillLogger.addHandler(self.commandLogger_handler)
        self.skillLogger.addHandler(self.fileLogger_Handler)

        WaitforNewOrder_1 = WaitforNewOrder(self)
        self.stateChange("WaitforNewOrder")
        currentState = WaitforNewOrder_1
        self.enabledState = self.skillDetails["enabled"]
        
        
        while (True):
            if ((currentState.__class__.__name__) == "WaitforNewOrder"):
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
                    if ((ts.__class__.__name__) == "WaitforNewOrder"):
                        self.currentConversationId = "temp"
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
    
    def geCurrentSKILLState(self):
        return self.SKILL_STATE
    
    def getListofSKILLStates(self):
        return self.SKILL_STATES
    
    
    def stateChange(self, STATE):
        self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        #self.sendMessage(self.statusMessage)
    
    def sendMessage(self, sendMessage):
        self.msgHandler.putObMessage(sendMessage)
    
    def receiveMessage(self,inMessage):
        try:    
            _conversationId = str(inMessage['frame']['conversationId'])
            senderRole = str(inMessage["frame"]['sender']['role']["name"])
            _messageType = str(inMessage['frame']['type'])
            if self.currentConversationId == "temp":
                if (senderRole == "ProductionManager"):
                    if (_messageType == "Order"):
                        self.QueueDict["Order"].put(inMessage)
                        self.currentConversationId = _conversationId
                else:
                    try:
                        self.QueueDict[_messageType].put(inMessage)
                        self.currentConversationId = _conversationId
                    except Exception as E:
                        self.skillLogger.info("Raise an Exception " + str(E))
            elif (self.currentConversationId == _conversationId):        
                try:
                    self.QueueDict[_messageType].put(inMessage)
                except Exception as E:
                    self.skillLogger.info("Raise an Exception " + str(E))
        except Exception as E:
            self.skillLogger.info("Raise an Exception " + str(E))



if __name__ == '__main__':
    
    lm2 = BoringRequester()
    lm2.Start('msgHandler')