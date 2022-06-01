'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

import sys
import time
import threading
import logging
import os

from dotenv import load_dotenv
from importlib import import_module
from dotenv.main import find_dotenv

try:
    from schedulers.propertiesScheduler import Scheduler
except ImportError:
    from  main.schedulers.propertiesScheduler import Scheduler

try:
    from datastore.datamanager import DataManager
except ImportError:
    from main.datastore.datamanager import DataManager

try:
    from handlers.messagehandler import MessageHandler
except ImportError:
    from main.handlers.messagehandler import MessageHandler
    
try:
    from config.aasxconfig import ConfigParser
except ImportError:
    from main.config.aasxconfig  import ConfigParser

try:
    from datastore.dbadaptor_custom import DB_ADAPTOR
except ImportError:
    from main.datastore.dbadaptor_custom import DB_ADAPTOR 

try:
    from utils.aaslog import serviceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import serviceLogHandler,LogList

class LIAPyAAS(object):

    def __init__(self):
        self.reset()
        self.endPointmodules = {}
        self.AASendPointHandles = {}
        self.assetaccessEndpointHandlers = {}
        self.aasSkillHandles = {}
        self.AASID = ''
        self.BroadCastMQTTTopic = ''
        self.msgHandler = MessageHandler(self)
        self.skillInstanceDictbyAASId = {}
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.lia_env_variable = {} 
        self.skilllogListDict = {}
        
        #  submodel template
        self.aasStandardSubmodelData = {}
        self.aasStandardSubmodelList = {}

        
        self.aasIdentificationIdList = {}
        self.heartBeatHandlerList = set()
        
        self.aasContentData = {}
        self.skillListWeb = {}
        self.AASData = []
        self.tdProperties = {}
        self.tdPropertiesList = {}
        
        self.pmIntancesDict = {}
        
        self.script_dir = (self.base_dir).split("src\main")[0]
        self.repository = os.path.join(self.script_dir, "config") 
        self.dataRepository = os.path.join(self.script_dir, "data")
        self.template_repository = os.path.join(self.script_dir, "config/templateInfo")
        self.downlaod_repository = os.path.join(self.script_dir, "config/aasx/files")
        
        self.img_repository = os.path.join(self.script_dir, "data/static/images")
        self.js_repository = os.path.join(self.script_dir, "data/static/js")
        self.css_repository = os.path.join(self.script_dir, "data/static/css")
        
        self.baseSkills = {}
        
    def reset(self):
        self.channels = {}
        self.io_adapters = {}
        self.AASendPointHandles = {}   
        self.scheduler = None

    def reconfigure(self):
        self.stop()
        self.reset()
        self.configure()
        self.start()
    
    ######## Configure Service Entities ##################
    
    def configureLogger(self):
        
        self.ServiceLogList = LogList()
        self.ServiceLogList.setMaxSize(maxSize= 200)
        
        self.serviceLogger = logging.getLogger(str(self.__class__.__name__) + ' Service Instance' )
        self.serviceLogger.setLevel(logging.DEBUG)
        
        self.commandLogger_handler = logging.StreamHandler()
        self.commandLogger_handler.setLevel(logging.DEBUG)

        self.fileLogger_Handler = logging.FileHandler(self.base_dir+"/logs/LIAPyAAS.LOG")
        self.fileLogger_Handler.setLevel(logging.DEBUG)
        
        self.listHandler_Handler = serviceLogHandler(self.ServiceLogList)
        self.listHandler_Handler.setLevel(logging.DEBUG)
        
        self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

        self.commandLogger_handler.setFormatter(self.Handler_format)
        self.listHandler_Handler.setFormatter(self.Handler_format)
        self.fileLogger_Handler.setFormatter(self.Handler_format)
        
        self.serviceLogger.addHandler(self.commandLogger_handler)
        self.serviceLogger.addHandler(self.listHandler_Handler)
        self.serviceLogger.addHandler(self.fileLogger_Handler)
        
        
        
        self.serviceLogger.info('The service Logger is Configured.')
    
    def configureAASConfigureParser(self):
        self.aasConfigurer = ConfigParser(self)
    
    def configureExternalVariables(self):
        load_dotenv(find_dotenv())
        self.aasConfigurer.setExternalVariables(os.environ)
        self.extHost = self.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        self.port = self.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
        self.exDomain = "http://"+self.extHost+":"+self.port+"/"
        print(self.exDomain)
        self.serviceLogger.info('External Variables are configured.')
        
    def configureAASID(self):
        self.AASID = "PyAASServer"
        self.serviceLogger.info('The AAS ID is configured.')

    def configureInternalVariables(self):
        self.registryAPI = ""
        self.productionSequenceList = {}
        self.productionStepList = {}
        self.conversationIdList = []
        self.aasList = {}
        self.aasIdList = []
        
    def configureDataAdaptor(self):
        self.dba = DB_ADAPTOR(self)

    def configureAASData(self):    
        configStatus = self.aasConfigurer.configureAASJsonData()
        if (configStatus):
            self.serviceLogger.info('The External DB is configured')
        else:
            self.shutDown()
            
    def confiureDataManager(self):
        self.dataManager = DataManager(self)

    def configureEndPoints(self):
        # configure Industrie 4.0 communication drivers
        aasEndPoints = self.aasConfigurer.getAASEndPoints()
        for endPoint in aasEndPoints:
            name = endPoint["Name"]
            module = endPoint["Module"]
            if module not in sys.modules:
                self.endPointmodules[module] = import_module("aasendpointhandlers"+module)
            
            endPoint0 = self.endPointmodules[module].AASEndPointHandler(self,self.msgHandler)
            self.AASendPointHandles[name] = endPoint0

            endPoint0.configure()
        
        self.serviceLogger.info('The AAS I40 End Points are configured')
 
        
    def configureAssetAccessPoints(self):
        # configure the IOAdapters
        assetAccessEndPoints = self.aasConfigurer.getAssetAccessEndPoints()
        for key in assetAccessEndPoints.keys():
            module = assetAccessEndPoints[key]
            if module not in sys.modules:
                self.assetmodule = import_module("assetaccessadapters"+module)
                endPoint0 = self.assetmodule.AsssetEndPointHandler(self)
                self.assetaccessEndpointHandlers[key] = endPoint0
        
        self.serviceLogger.info('The Asset Access points are configured')

    def configureRegisterSKill(self):
        registerModule = import_module("." + "Register", package="skills")
        registerBaseCLass = getattr(registerModule, "Register")
        return registerBaseCLass(self)
        
    def configurePMSkill(self):
        pManagerModule = import_module("." + "ProductionManager", package="skills")
        pmBaseCLass = getattr(pManagerModule, "ProductionManager")
        return pmBaseCLass(self)
    
    def configureSkills(self): 
        #configure skills
        self.aasSkills = self.aasConfigurer.GetAAsxSkills()
        for aasIndex in self.aasSkills.keys():
            self.skillDetails = self.aasSkills[aasIndex]
            skillList = []
            self.skillInstanceDictbyAASId[aasIndex] =  {}
            for skill in self.skillDetails.keys():
                skillModule = import_module("." + skill, package="skills")
                skillBaseclass_ = getattr(skillModule, skill)
                skillInstance = skillBaseclass_(self)
                self.skillInstanceDictbyAASId[aasIndex][skill] = {"skillInstance":skillInstance,"skillDetails":self.skillDetails[skill]}
                skillList.append(skill)
            skillList.append("Register")
            skillList.append("Production Manager")
            self.skillInstanceDictbyAASId[aasIndex]["ProductionManager"] = {"skillInstance":self.configurePMSkill(),"skillDetails":{"SkillName" : "Register","SkillService" : "Registration","InitialState" : "WaitforNewOrder","enabled" :"Y"}}
            self.skillInstanceDictbyAASId[aasIndex]["Register"] = {"skillInstance":self.configureRegisterSKill(),"skillDetails":{"SkillName" : "ProductionManager","SkillService" : "Production Manager","InitialState" : "WaitforNewOrder","enabled" : "Y"}}
            self.skillListWeb[aasIndex] = skillList
            self.serviceLogger.info('The skills are configured')
        print("djdjdjd")
        
    def configureLogList(self):
        for aasIndex in self.skillInstanceDictbyAASId.keys():
            skillLogs = {}
            for skill in self.skillInstanceDictbyAASId[aasIndex].keys():
                skillLogs[skill] = LogList()
            self.skilllogListDict[aasIndex] = skillLogs
    
    def configureSkillWebList(self):
        i = 0
        for skillWeb in self.skillListWeb:
            #if skillWeb == "ProductionManager":
            #    del self.skillListWeb[i]
            #    break
            i = i + 1
        
    
    def getSubmodelPropertyListDict(self,aasIdentifier):
        self.submodelPropertyListDict = self.aasConfigurer.getSubmodelPropertyListDict(aasIdentifier)
        return self.submodelPropertyListDict
        
    def getSubmodelList(self,aasIdentifier):
        self.submodelList = self.aasConfigurer.getSubmodelPropertyList(aasIdentifier)
        return self.submodelList
    ####### Start Service Entities ################
        
    def startEndPoints(self):
        self.AASendPointHandlerObjects = {}
        for module_name, endPointHandler in self.AASendPointHandles.items():
            endPointHandler.start()
            self.AASendPointHandlerObjects[module_name] = endPointHandler
            
        self.serviceLogger.info('The AAS end Points are Started')
        
    def startAssetEndPoints(self):
        self.serviceLogger.info('The Asset end Points are Started')
    
    def startMsgHandlerThread(self):
        msgHandlerThread = threading.Thread(target=self.msgHandler.start,name="msgHandler", args=(self.skillInstanceDictbyAASId,self.AASendPointHandlerObjects,))     
        msgHandlerThread.start()
    
        self.serviceLogger.info('The message handler started')
    
    def startScheduler(self):
        self.scheduler.start()
        self.serviceLogger.info('The Job Scheduler is Started')

    def startSkills(self):      
        # Start remaining skills that are part of the skill instance list
        for aasIndex in self.skillInstanceDictbyAASId.keys():
            for skill in self.skillInstanceDictbyAASId[aasIndex]:
                skillInfo = self.skillInstanceDictbyAASId[aasIndex][skill] 
                skillInstance = skillInfo["skillInstance"]
                skillDetails = skillInfo["skillDetails"]
                threading.Thread(target=skillInstance.Start, args=(self.msgHandler, skillDetails,aasIndex,),name =str(aasIndex)+skill).start()
        
        self.serviceLogger.info('The Skills are Started')
    
    def startDataManager(self):
        dataManagerThread = threading.Thread(target=self.dataManager.start, args=(),name="DataManager")     
        dataManagerThread.start()
        self.serviceLogger.info('The message handler started')
    
    def startHeartBeatHandler(self):
        heartBeatThread = threading.Thread(target=self.msgHandler.trigggerHeartBeat)
        heartBeatThread.start()
    
    def configure(self):
        
        self.commList = [] # List of communication drivers
        self.skilLList = [] # List of Skills
        self.skillInstanceList = {} # List consisting of instances of skills

        #configure Service Logger
        self.configureLogger()
        self.serviceLogger.info('Configuring the Service Entities.')
        #configure AASXConfigParser
        self.configureAASConfigureParser() 
        #configure AASID
        self.configureAASID()
        #configure External Variables
        self.configureExternalVariables()
        #configure registryAPI
        self.configureInternalVariables()
        self.serviceLogger.info("Configuration Parameters are Set.")

        #configure Data Adaptor
        self.configureDataAdaptor()
        #configure the Data Manager
        self.confiureDataManager()
        self.configureAASData()
        #configure EndPoints
        self.configureEndPoints()
        #configure IA Adaptors
        self.configureAssetAccessPoints()
        #configure Skill       
        self.configureSkills()
        #configure Logs
        self.configureLogList()
        #configure skill web list
        self.configureSkillWebList()
        #configure submodel properties
        #self.configureSubmodelProperties()   
        # configure the scheduler
        self.scheduler = Scheduler(self)
        self.scheduler.configure()
        
        
    def start(self):
        
        self.serviceLogger.info('Starting the Service Entities')
        
        self.cdrivers = {}
        self.cdrv_mqtt = None
        #start the Data Manager
        self.startDataManager()
        #start the communication drivers
        self.startEndPoints()
        #start the message handler thread
        self.startMsgHandlerThread()
        # start the scheduler
        self.startScheduler()
        #start the skills
        self.startSkills()
        #heartBeatHandler
        self.startHeartBeatHandler()
    
    def stop(self):
        self.scheduler.stop()
        for module_name, cdrv in self.cdrvs.items():
            cdrv.stop()
    
    def shutDown(self):
        self.serviceLogger.info("The Service Logger is shutting down.")
        os._exit(0)

if __name__ == "__main__":
    pyAAS = LIAPyAAS()
    pyAAS.configure()
    pyAAS.start()
    print('Press Ctrl+{0} to exit'.format('C'))
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        pyAAS.stop()

