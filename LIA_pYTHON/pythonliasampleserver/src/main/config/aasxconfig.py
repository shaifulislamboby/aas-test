'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import json
import os.path

try:
    from utils.utils import AASDescriptor
except ImportError:
    from main.utils.aaslog import AASDescriptor

try:
    from config.TemplateCapture import NameplateCapture,IdentificationCapture,DocumentCapture,TechnicalDataCapture
except ImportError:
    from main.config.TemplateCapture import NameplateCapture,IdentificationCapture,DocumentCapture,TechnicalDataCapture
    

enabledState = {"Y":True, "N":False}

class ConfigParser(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.jsonData = {}
        self.templateData = {}
        self.baseFile = "TestSample.json"     
        with open(os.path.join(self.pyAAS.repository, "TestSample.json"), encoding='utf-8') as json_file:
            self.jsonData = json.load(json_file)
        with open(os.path.join(self.pyAAS.template_repository, "documentationInfo.json"), encoding='utf-8') as json_file_document:
            self.templateData["Documentation"] = json.load(json_file_document)
        with open(os.path.join(self.pyAAS.template_repository, "namplateInfo.json"), encoding='utf-8') as json_file_nameplate:
            self.templateData["Nameplate"] = json.load(json_file_nameplate)
        with open(os.path.join(self.pyAAS.repository,"ass_JsonSchema.json"), encoding='utf-8') as json_file_aas:
            self.aasJsonSchema  = json.load(json_file_aas)
        with open(os.path.join(self.pyAAS.repository,"aasShell_JsonSchema.json"), encoding='utf-8') as json_file_aasShell:
            self.aasShell_JsonSchema  = json.load(json_file_aasShell)
        with open(os.path.join(self.pyAAS.repository,"asset_JsonSchema.json"), encoding='utf-8') as json_file_asset:
            self.assetJsonSchema  = json.load(json_file_asset)
        with open(os.path.join(self.pyAAS.repository,"submodel_JsonSchema.json"), encoding='utf-8') as json_file_submodel:
            self.submodelJsonSchema  = json.load(json_file_submodel)
        with open(os.path.join(self.pyAAS.repository,"conceptDescription_JsonSchema.json"), encoding='utf-8') as json_file_submodel:
            self.conceptDescription_JsonSchema  = json.load(json_file_submodel)
        with open(os.path.join(self.pyAAS.base_dir,"config/status.json"), encoding='utf-8') as statusFile:
            self.submodel_statusResponse  = json.load(statusFile)
        with open(os.path.join(self.pyAAS.base_dir,"config/SrSp.json"), encoding='utf-8') as SrSp_Path:
            self.SrSp  = json.load(SrSp_Path)    
            del self.SrSp["temp"]
        with open(os.path.join(self.pyAAS.dataRepository,"database.json"), encoding='utf-8') as json_file_dataBase:
            self.dataBaseFile  = json.load(json_file_dataBase)
        
            
    def getStatusResponseSubmodel(self):
        return self.submodel_statusResponse
        
    def setExternalVariables(self,environ):
        for env_variable in environ.keys():
            try:
                if (env_variable.split("_")[0] == "LIA"):
                    self.pyAAS.lia_env_variable[env_variable] = os.environ[env_variable]
            except Exception as E:
                pass

    def configureAASJsonData(self):
        try:
            colCheck = self.pyAAS.dba.AAS_Database_Server.checkforExistenceofColumn("AASX")         
            if (colCheck == "empty column"):
                self.pyAAS.dba.updateAASDataColumn(self.jsonData)
            elif (colCheck == "data present"):
                self.pyAAS.dba.deleteAASDataColumn()
                self.pyAAS.dba.updateAASDataColumn(self.jsonData)
            elif (colCheck == "column not present"):
                self.pyAAS.dba.createNewDataBaseColumn("AASX")
                self.pyAAS.dba.updateAASDataColumn(self.jsonData)
            self.pyAAS.dba.updateAASDataList()
            self.getStandardSubmodels()
            self.aasIdList()
            self.getAASList()
            return True    
        except Exception as E:
            self.pyAAS.serviceLogger.info('Error configuring the database' + str(E))
            return False        
    
    def getStandardSubmodels(self):
        for aasIndex in self.pyAAS.aasContentData.keys():
            self.stdSubmodelData = {}
            self.stdSubmodelList = []
            aasN = self.pyAAS.aasContentData[aasIndex]
            for submodel in aasN["submodels"]:
                if submodel["idShort"] == "Nameplate":
                    self.stdSubmodelData["NAMEPLATE"]  = self.getNamePlateData(submodel)
                    self.stdSubmodelList.append("NAMEPLATE")
                elif "Documentation" in submodel["idShort"]:
                    self.stdSubmodelData["DOCUMENTATION"]  = self.getDcumentationData(submodel)
                    self.stdSubmodelList.append("DOCUMENTATION")
                elif submodel["idShort"] == "TechnicalData":
                    self.stdSubmodelData["TECHNICAL_DATA"]  = self.getTechnicalData(submodel)
                    self.stdSubmodelList.append("TECHNICAL_DATA")
                if submodel["idShort"] == "Identification":
                    self.stdSubmodelData["IDENTIFICATION"]  = self.getIdentificationData(submodel)
                    self.stdSubmodelList.append("IDENTIFICATION")
                if submodel["idShort"] == "ThingDescription":
                    self.stdSubmodelData["THING_DESCRIPTION"]  = self.configureThingDescriptionProperties(submodel,aasN["identification"]["id"],aasIndex)
                    self.stdSubmodelList.append("THING_DESCRIPTION")
            self.pyAAS.aasStandardSubmodelData[aasIndex] = self.stdSubmodelData
            self.pyAAS.aasStandardSubmodelList[aasIndex] = self.stdSubmodelList

    def aasIdList(self):
        for aasIndex in self.pyAAS.aasContentData.keys():
            _id = self.pyAAS.aasContentData[aasIndex]["identification"]["id"]
            self.pyAAS.aasIdentificationIdList[_id] = aasIndex    
    
    def getAASEndPoints(self):
        aasEndpointsList = []
        moduleDict = {"MQTT":".mqtt_endpointhandler","RESTAPI":".restapi_endpointhandler"}
        for moduleName in moduleDict.keys():
            aasEndpointsList.append({"Name":moduleName,"Module":moduleDict[moduleName]})
        return aasEndpointsList

    def getAssetAccessEndPoints(self):
        return {"OPCUA":".io_opcua"}

    
    def getpropertyValue(self,submodelElement):
        check = True
        if (submodelElement["modelType"]["name"] == "MultiLanguageProperty"):
            for lang in submodelElement["value"]["langString"]: 
                if lang["language"] == "de":
                    return lang["text"]
            if (check):
                return submodelElement["langString"]["0"]["value"]
        else:
            return submodelElement["value"]
    
    def reOrderEntityList(self,documentationList):
        numberofDocuments =len(documentationList)
        if numberofDocuments == 0:
            return []
        elif numberofDocuments == 1:
            return  [[documentationList[0]]]
        else:
            documentDivisions = []
            if ((numberofDocuments % 2) == 0):
                for i in range(1,int(numberofDocuments/2)+1):
                    tempList = []
                    tempList.append(documentationList[2*i-2])
                    tempList.append(documentationList[2*i-1])
                    documentDivisions.append(tempList)
                return documentDivisions
            else: 
                numberofRows = int( (numberofDocuments + 1)/ 2)
                for i in range(1,numberofRows):
                    tempList = []
                    tempList.append(documentationList[2*i-2])
                    tempList.append(documentationList[2*i-1])
                    documentDivisions.append(tempList)
                documentDivisions.append([documentationList[numberofDocuments-1]])
                return documentDivisions

    def GetAAsxSkills(self):
        skillListAAS= {}
        for aasIndex in self.pyAAS.aasContentData.keys():
            skillsDict = {}
            aasN = self.pyAAS.aasContentData[aasIndex]
            stepList = []
            for subnmodel in aasN["submodels"]:
                if subnmodel["idShort"] == "OperationalData":
                    for eachskill in subnmodel["submodelElements"]:
                        skillName = ""
                        skill = {}
                        for skillDetails in eachskill["value"]: 
                            if (skillDetails["idShort"] == "SkillName"):
                                skill[skillDetails["idShort"]] = skillDetails["value"]
                                skillName = skillDetails["value"]
                            if (skillDetails["idShort"] == "SkillService"):
                                skill[skillDetails["idShort"]] = skillDetails["value"]
                            if (skillDetails["idShort"] == "InitialState"):
                                skill[skillDetails["idShort"]] = skillDetails["value"]
                            if (skillDetails["idShort"] == "enabled"):
                                skill[skillDetails["idShort"]] = enabledState[skillDetails["value"]] 
                        skillsDict[skillName] = skill
                        if (self.checkForOrderExistence(skill)):
                            stepList.append(skillName)
            else:
                pass                   

            
            for key in self.SrSp.keys():
                skillsDict[key] = self.SrSp[key]
                if (self.checkForOrderExistence(self.SrSp[key])):
                    stepList.append(key)
        
            stepList.append("Register")
            skillListAAS[aasIndex] = skillsDict
            self.pyAAS.productionStepList[aasIndex] = stepList
        return skillListAAS 
    
    def getAASList(self):
        try:
            aasList = []
            self.pyAAS.AASData = []
            i = 0
            for aasId in self.pyAAS.aasContentData:
                aasList.append({"aasId":aasId,"idShort":self.pyAAS.aasContentData[aasId]["idShort"]}) 
            numberofAAS = len(aasList)
            if numberofAAS == 0:
                self.pyAAS.AASData.append([])
            elif numberofAAS == 1:
                self.pyAAS.AASData.append(aasList)
            else:
                aasDivisions = []
                if ((numberofAAS % 2) == 0):
                    for i in range(1,int(numberofAAS/2)+1):
                        tempList = []
                        tempList.append(aasList[2*i-2])
                        tempList.append(aasList[2*i-1])
                    self.pyAAS.AASData.append(tempList)
                else: 
                    numberofRows = int( (numberofAAS + 1)/ 2)
                    for i in range(1,numberofRows):
                        tempList = []
                        tempList.append(aasList[2*i-2])
                        tempList.append(aasList[2*i-1])
                        self.pyAAS.AASData.append(tempList)
                    self.pyAAS.AASData.append([aasList[numberofAAS-1]])

        except:         
            return self.pyAAS.AASData
        
    def getRelevantSubModel(self,submodelId):
        checkVar = False
        for submodel in self.jsonData["submodels"]:         
            if (submodel["identification"]["id"] == submodelId):
                checkVar = True
                return {"data" : submodel, "check" : True}
        if(not checkVar):
            return {"check" : False}
        
    def GetAAS(self):
        return self.jsonData
       
    def getSubModelbyID(self,sbIdShort):
        checkVar = True
        for submodel in self.jsonData["submodels"]:         
            if (submodel["idShort"] == sbIdShort):
                checkVar = False
                return submodel
        if(checkVar):
            return {"message": "Submodel with the given IdShort is not part of this AAS","status": 400}
    
  
    def getQualifiersList(self,submodelElem):
        qualiferList = {}
        if "constraints" in list(submodelElem.keys()):
            for qualifier in submodelElem["constraints"]:
                qualiferList[qualifier["type"]] = qualifier["value"]
        return (qualiferList)
    
    def getSemanticIdList(self,submodelElem):
        semanticIdList = {}
        if "semanticId" in list(submodelElem.keys()):        
            for semId in submodelElem["semanticId"]["keys"]:
                semanticIdList[semId["type"]]  = semId["value"]
        return (semanticIdList)
    
    def parseBlobData(self,mimeType,data):
        if (mimeType == "application/json"):
            jData =  json.loads(data)
            return jData
        else: 
            return data
        
    def processSubmodelELement(self,submodelElement,submodelProperetyDict,idShortPath):
            if submodelElement["modelType"]["name"] == "SubmodelElementCollection":
                collectionDict = {}
                for elem in submodelElement["value"]: 
                    collectionDict = self.processSubmodelELement(elem,collectionDict,idShortPath + "."+elem["idShort"])
                submodelProperetyDict[submodelElement["idShort"]] =  { "data" :  collectionDict,"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement), "type" : "collection" }
            elif (submodelElement["modelType"]["name"] == "Property"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Property","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "Range"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"min" : submodelElement["min"],"max" : submodelElement["max"] },"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Range","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "MultiLanguageProperty"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"MultiLanguageProperty","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "File"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"File","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "Blob"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : self.parseBlobData(submodelElement["mimeType"], submodelElement["value"]), "mimeType" :submodelElement["mimeType"], "qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Blob","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "ReferenceElement"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"ReferenceElement","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "RelationshipElement"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"first" : submodelElement["first"],"second" : submodelElement["second"]},"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"RelationshipElement","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "AnnotatedRelationshipElement"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"first" : submodelElement["first"],"second" : submodelElement["second"]},"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"AnnotatedRelationshipElement","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "Capability"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : "Capability","qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Capability","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "Operation"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"inputVariable" : submodelElement["inputVariable"],"outputVariable" : submodelElement["outputVariable"],"inoutputVariable" : submodelElement["inoutputVariable"]},"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Operation","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "BasicEvent"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["observed"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"BasicEvent","idShortPath":idShortPath}
            elif (submodelElement["modelType"]["name"] == "Entity"):     
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["statements"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Entity","idShortPath":idShortPath}    
            return submodelProperetyDict
            
    def getSubmodePropertyDict(self,submodel):
        submodelProperetyDict = {}
        for eachSubmodelElem in submodel["submodelElements"]:
            self.processSubmodelELement(eachSubmodelElem,submodelProperetyDict,eachSubmodelElem["idShort"])
        return submodelProperetyDict
    
    def getSubmodelPropertyList(self,aasIdentifier):
        submodelNameList = []
        for submodel in self.pyAAS.aasContentData[aasIdentifier]["submodels"]:
            submodelNameList.append(submodel)
        return submodelNameList
    
    def getSubmodelPropertyListDict(self,aasIdentifier):
        submodelPropertyListDict = {}
        i = 0
        submodelList = self.getSubmodelPropertyList(aasIdentifier)
        for submodel in submodelList:
            submodelName =  submodel["idShort"]
            if not (submodelName in ["Mechanical break down","Nameplate","TechnicalData","ManufacturerDocumentation","Identification"]):
                submodelProperetyDict = self.getSubmodePropertyDict(submodel)    
                if (i == 0):
                    status = " fade show active"
                    i = 1        
                else:
                    status = " fade show"
                submodelPropertyListDict[submodelName] = {"status" : status,
                                                          "data" : submodelProperetyDict,
                                                          "type" : "collection"
                                                         }
        return submodelPropertyListDict
    
    def configureDescriptor(self,identifier):
        aasDesc = AASDescriptor(self.pyAAS)
        aasIndex = self.pyAAS.aasIdentificationIdList[identifier]
        return aasDesc.createDescriptor(aasIndex)

    def checkForOrderExistence(self,skill):
        if (skill["InitialState"] == "WaitforNewOrder"):
            return True
        else :
            return False
    
    def checkSubmodelwithOnlyPropeties(self,submodelName):
        returnData = self.getRelevantSubModel(submodelName)
        try:
            if returnData["check"] :
                submodelData = returnData["data"]
                for submodelElement in submodelData["submodelElements"]:
                    if submodelElement["modelType"]["name"] == "Property":
                        pass
                    else:
                        return False
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error "+ str(E))
            return False      
          
    def saveToDatabase(self,dataJ,colName):
        try:
            if colName == "AASX":
                dataC = {"Test":"123"}
                if len(dataJ["AASX"]) != 0 :
                    dataC = dataJ["AASX"][0]
                with open(os.path.join(self.pyAAS.repository,self.baseFile), 'w', encoding='utf-8') as databaseFile1:
                    json.dump(dataC, databaseFile1, ensure_ascii=False, indent=4)                
            with open(os.path.join(self.pyAAS.dataRepository,"database.json"), 'w', encoding='utf-8') as databaseFile2:
                json.dump(dataJ, databaseFile2, ensure_ascii=False, indent=4)
                return {"message":"success"}
        except Exception as E: 
            self.pyAAS.serviceLogger.info("Error at saveToDatabase"+ str(E))
            return {"message":"failure"}

    def configureThingDescriptionProperties(self,submodel,aasIdenId,aasIndex):
        tdProperties = []
        updateFrequency = 60
        unit = ""
        for tdELement in submodel["submodelElements"]:
            if (tdELement["idShort"] == "properties"):
                for tdproperty in tdELement["value"]:
                    for pConstraint in tdproperty["constraints"]:
                        if(pConstraint["type"] == "updateFrequencey"):
                            updateFrequency = pConstraint["value"]
                        if(pConstraint["type"] == "unit"):
                            unit = pConstraint["value"]   
                                                                
                    for pelem in tdproperty["value"]:
                        if(pelem["idShort"] == "forms"):
                            for formConstraint in pelem["value"][0]["constraints"]:
                                if (formConstraint["type"] == "href"):
                                    tddata ={"propertyName" :  tdproperty["idShort"],
                                             "href" : formConstraint["value"],
                                             "updateFrequency": updateFrequency,
                                             "submodelName" : submodel["idShort"],
                                             "aasId" : aasIdenId,
                                             "aasIndex" : aasIndex,
                                             "unit" : unit,
                                             "value" : [0,0,0,0,0,0,0,0,0,0],
                                             "label" : [0,0,0,0,0,0,0,0,0,0],
                                             "idShortPath" : "properties."+tdproperty["idShort"]}
                                    tdProperties.append(tddata)
                                    self.pyAAS.tdPropertiesList[tdproperty["idShort"]+"_aasId"+str(aasIndex)]  = tddata
        return self.reOrderEntityList(tdProperties)

    
    def getDcumentationData(self,submodel):
        documentationList = []
        documentLangSet = set([])
        languageDIct = {}        
        for eachDocument in submodel["submodelElements"]:
            tc = DocumentCapture(eachDocument,"Documentation",self.pyAAS)
            documentData = tc.getTemplateInformation()
            documentationList.append(documentData)
            for lang in documentData["languageSet"]:
                documentLangSet.add(lang)
        for dLang in documentLangSet:
            languageDIct[dLang] = []
        for docData in documentationList:
            for lang in docData["languageSet"]:
                if lang in languageDIct.keys():
                    languageDIct[lang].append(docData["data"])
                        
        documentationData = {}
        i = 0
        active = "active"
        status = "true"
        showActive = " show active"
        for lang in languageDIct.keys():
            if i == 0:
                i = i + 1
            else:
                status = "false"
                active = ""
                showActive = ""
            documentationData[lang]  = {"data":self.reOrderEntityList(languageDIct[lang]),"active":active,"status":status,"showActive":showActive}              
        return documentationData
              
    def getNamePlateData(self,submodel):
        tc = NameplateCapture(submodel,self.pyAAS)
        return tc.getTemplateInformation()      
 
    def getIdentificationData(self,submodel):
        tc = IdentificationCapture(submodel,self.pyAAS)
        return tc.getTemplateInformation()
           
    def getTechnicalData(self,submodel):
        tc = TechnicalDataCapture(submodel,self.pyAAS)
        return tc.getTemplateInformation()

 
                