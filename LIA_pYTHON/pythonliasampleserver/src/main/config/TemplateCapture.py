'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

    
class NameplateCapture(object):
    
    def __init__(self,namePlateSubmodel,pyAAS):
        self.namePlateSubmodel = namePlateSubmodel
        self.pyAAS = pyAAS
        self.nameplateData = {"EN":{},"DE":{}}
    
    
    def createPropertyInformation(self,propertyElem,idShort):
        self.nameplateData["EN"][idShort] = propertyElem["value"]
        self.nameplateData["DE"][idShort] = propertyElem["value"]
    
    def createMultiLanguagePropertyInformation(self,multiLanguagePEleme,idShort):
        for langString in  multiLanguagePEleme["value"]["langString"]:
            if langString["language"].upper() == "EN":
                self.nameplateData["EN"][idShort] = langString["text"]
            elif langString["language"].upper() == "DE":
                self.nameplateData["DE"][idShort] = langString["text"]
    
    def createFileElementInformation(self,fileElem,idShort):
        self.nameplateData["EN"][idShort] = fileElem["value"]
        self.nameplateData["DE"][idShort] = fileElem["value"] 
    
    def captureNamePlateElem(self,nameplateElem,idShort):
        categoryName = nameplateElem["modelType"]["name"]
        if categoryName == "Property" :
            self.createPropertyInformation(nameplateElem,idShort)
        if categoryName == "MultiLanguageProperty":
            self.createMultiLanguagePropertyInformation(nameplateElem,idShort)
        if categoryName == "File" :
            self.createFileElementInformation(nameplateElem,idShort)
    
    def captureMarkings(self,marking):
        markingData = {}
        extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
        for markingELem in marking["value"]:
            if markingELem["idShort"] == "MarkingName":
                markingData["MarkingName"] = markingELem["value"]
            elif markingELem["idShort"] == "MarkingFile":
                if markingELem["value"] != "":
                    markingData["MarkingFile"] = "http://"+extHost+":"+str(port)+"/static/"+(markingELem["value"]).split("/")[-1]
                else:
                    markingData["MarkingFile"] = ""
            else:               
                markingData[markingELem["idShort"]] = markingELem["value"]
        return markingData   
                    
    def captureCategoryELements(self):
        for nameplateElem in self.namePlateSubmodel["submodelElements"]:
            if nameplateElem["modelType"]["name"] ==  "SubmodelElementCollection":
                if  nameplateElem["idShort"] == "Address":
                    for addressElem in nameplateElem["value"]:
                        if addressElem["modelType"]["name"] ==  "SubmodelElementCollection":
                            for addressSubElem in addressElem["value"]:
                                self.captureNamePlateElem(addressSubElem,addressSubElem["idShort"])
                        else:
                            self.captureNamePlateElem(addressElem,addressElem["idShort"])
                elif nameplateElem["idShort"] == "AssetSpecificProperties":
                    AssetSpecificProperties = {}
                    for aspELem in nameplateElem["value"]:
                        AssetSpecificProperties[aspELem["idShort"]] = aspELem["value"][0]["value"]
                                                                      
                    self.nameplateData["EN"]["AssetSpecificProperties"] = AssetSpecificProperties
                    self.nameplateData["DE"]["AssetSpecificProperties"] = AssetSpecificProperties 
                         
                elif nameplateElem["idShort"] == "Markings":
                    markigsList = []
                    for marking in nameplateElem["value"]:
                        markigsList.append(self.captureMarkings(marking))
                    self.nameplateData["EN"]["Markings"] = markigsList
                    self.nameplateData["DE"]["Markings"] = markigsList 
     
            else:       
                self.captureNamePlateElem(nameplateElem,nameplateElem["idShort"])              
    
    def reOrderNamePlate(self):
        reOrderedNamePlate = {}
        _enNamePlate = {}
        _deNamePlate = {}
        _deNamePlate["active"] = "active"
        _deNamePlate["status"] = "true"
        _deNamePlate["showActive"] = " show active"
        _deNamePlate["data"] = self.nameplateData["DE"]
       
        _enNamePlate["active"] = ""
        _enNamePlate["status"] = "false"
        _enNamePlate["showActive"] = ""
        _enNamePlate["data"] = self.nameplateData["EN"]
        
        reOrderedNamePlate["DE"] = _deNamePlate
        reOrderedNamePlate["EN"] = _enNamePlate
        
        return reOrderedNamePlate
        
    def getTemplateInformation(self):
        self.templateInfo = self.pyAAS.aasConfigurer.templateData["Nameplate"]
        self.captureCategoryELements()
        return self.reOrderNamePlate()
    

class IdentificationCapture(object):
    
    def __init__(self,identificationSubmodel,pyAAS):
        self.identificationSubmodel = identificationSubmodel
        self.pyAAS = pyAAS
        self.identificationData = {}
    
    
    def createPropertyInformation(self,propertyElem,idShort):
        self.identificationData[idShort] = propertyElem["value"]
    
    def createFileElementInformation(self,fileElem,idShort):
        extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
        if (fileElem["value"] != ""):
            self.identificationData[idShort] = "http://"+extHost+":"+str(port)+"/static/"+fileElem["value"].split("/")[-1]
        else:
            self.identificationData[idShort] = ""
            
    def captureIDElem(self,nameplateElem,idShort):
        categoryName = nameplateElem["modelType"]["name"]
        if categoryName == "Property" :
            self.createPropertyInformation(nameplateElem,idShort)
        if categoryName == "File" :
            self.createFileElementInformation(nameplateElem,idShort)
    
    def captureCategoryELements(self):
        contactInfos = {}
        for idELem in self.identificationSubmodel["submodelElements"]:
            if idELem["modelType"]["name"] ==  "SubmodelElementCollection":
                contact = {}
                for contactElement in idELem["value"]:
                    if contactElement["modelType"]["name"] ==  "SubmodelElementCollection":
                        #physicalAdd = {}
                        for physicalAddressElem in contactElement["value"]:
                            contact[physicalAddressElem["idShort"]] = physicalAddressElem["value"]
                        #contact["PhysicalAddress"] = physicalAdd
                    else:
                        contact[contactElement["idShort"]] = contactElement["value"]
                contactInfos[idELem["idShort"]] = contact
            else:       
                self.captureIDElem(idELem,idELem["idShort"])              
        self.identificationData["contactInfo"] = contactInfos
        
    def getTemplateInformation(self):
        self.captureCategoryELements()
        return self.identificationData

   
class DocumentCapture(object):
    
    def __init__(self,documentSubmodel,templateName,pyAAS):
        self.documentSubmodel = documentSubmodel
        self.templateName = templateName
        self.pyAAS = pyAAS
        self.documentInstance = {}

    def captureCategoryELements(self):
        languageSet = set([])
        documentData = {}
        DocumentIdDomain = {}
        documentVersion = {}
        DocumentClassification = {}
        for docElem in self.documentSubmodel["value"]:
            if docElem["idShort"] == "DocumentVersion":
                for docSubmElem in docElem["value"]:
                    if docSubmElem["idShort"][0:8] == "Language":
                        documentVersion[docSubmElem["idShort"]] = docSubmElem["value"].upper()
                        languageSet.add(docSubmElem["value"].upper())
                    else:
                        if docSubmElem["modelType"]["name"] == "MultiLanguageProperty":
                            langString = {}
                            for _langString in  docSubmElem["value"]["langString"]:
                                langString[_langString["language"].upper()] = _langString["text"]
                            documentVersion[docSubmElem["idShort"]] = langString
                        else:
                            documentVersion[docSubmElem["idShort"]] = docSubmElem["value"]
            
            if docElem["idShort"][0:16] == "DocumentIdDomain": 
                _documentIDomain = {}
                for subElem in docElem["value"]:
                    _documentIDomain[subElem["idShort"]] = subElem["value"]
                DocumentIdDomain[docElem["idShort"]] = _documentIDomain
            
            if docElem["idShort"][0:22] == "DocumentClassification": 
                _documentClassification = {}
                for subElem in docElem["value"]:
                    _documentClassification[subElem["idShort"]] = subElem["value"]
                DocumentIdDomain[docElem["idShort"]] = _documentClassification        
        
        documentData["DocumentVersion"] =  documentVersion
        documentData["DocumentIdDomain"] =  DocumentIdDomain
        documentData["DocumentClassification"] =  DocumentClassification
        documentData["documentIdShort"] =  self.documentSubmodel["idShort"]
        
        self.documentInstance["languageSet"] = languageSet
        self.documentInstance["data"] = documentData
        
        
    def getTemplateInformation(self):
        self.templateInfo = self.pyAAS.aasConfigurer.templateData[self.templateName]
        self.captureCategoryELements()
        return self.documentInstance      
    

class TechnicalDataCapture(object):
    
    def __init__(self,technicalDataSubmodel,pyAAS):
        self.technicalDataSubmodel = technicalDataSubmodel
        self.pyAAS = pyAAS
        self.technicalData = {}

    def createPropertyInformation(self,propertyElem):
        return propertyElem["value"]
    
    def createFileElementInformation(self,fileElem):
        extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
        if (fileElem["value"] != ""):
            return "http://"+extHost+":"+str(port)+"/static/"+fileElem["value"].split("/")[-1]
        else:
            return ""
            
    def captureTDElem(self,elem):
        categoryName = elem["modelType"]["name"]
        if categoryName == "Property" :
            return self.createPropertyInformation(elem)
        if categoryName == "File" :
            return self.createFileElementInformation(elem)
    
    def captureCategoryELements(self):
        for tdElem in self.technicalDataSubmodel["submodelElements"]:
            if tdElem["idShort"] == "GeneralInformation":      
                generalInformation = {}
                productImages = {}
                for giElem in tdElem["value"]:
                    if (giElem["idShort"])[0:12] == "ProductImage":
                        productImages[giElem["idShort"]] = self.captureTDElem(giElem)
                    else:
                        generalInformation[giElem["idShort"]] = self.captureTDElem(giElem)
                generalInformation["ProductImages"] = productImages
                self.technicalData["GeneralInformation"] = generalInformation
                    
            elif tdElem["idShort"] == "ProductClassifications":      
                ProductClassifications = {}
                for pcsElem in tdElem["value"]:
                    pClassification = {}
                    for pcElem in pcsElem["value"]:
                        pClassification[pcElem["idShort"]] = self.captureTDElem(pcElem)
                    ProductClassifications[pcsElem["idShort"]] = pClassification
                self.technicalData["ProductClassifications"] = ProductClassifications
                
            elif tdElem["idShort"] == "TechnicalProperties":      
                technicalProperties = {}
                for tcpropertyElem in tdElem["value"]:
                    if isinstance(tcpropertyElem["value"], list):
                        tcProperty = {}
                        for tpElem in tcpropertyElem["value"]:
                            tcProperty[tpElem["idShort"]] = self.captureTDElem(tpElem)
                        technicalProperties[tcpropertyElem["idShort"]] = tcProperty
                    else:
                        technicalProperties[tcpropertyElem["idShort"]] = tcpropertyElem["value"]
                self.technicalData["TechnicalProperties"] = technicalProperties
                
            elif tdElem["idShort"] == "FurtherInformation":      
                furtherInformation = {}
                for fiElem in tdElem["value"]:
                    furtherInformation[fiElem["idShort"]] = self.captureTDElem(fiElem)
                    self.technicalData["FurtherInformation"] = furtherInformation
                    
    def getTemplateInformation(self):
        self.captureCategoryELements()
        return self.technicalData
    