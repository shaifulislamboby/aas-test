'''
Copyright (c) 2021-2022 Otto-von-Guericke-Universitat Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
try:
    from datastore.aas_database_server import AAS_Database_Server
except ImportError:
    from main.datastore.aas_database_server import AAS_Database_Server

class DB_ADAPTOR(object):
    '''
    classdocs
    '''

    def __init__(self,pyAAS):
        '''
        Constructor
        '''
        self.pyAAS = pyAAS
        self.AAS_Database_Server = AAS_Database_Server(self.pyAAS)   

        self.col_AASX = self.AAS_Database_Server.createNewDataBaseColumn("AASX")
        self.col_Messages = self.AAS_Database_Server.createNewDataBaseColumn("messages")
        
        
## AAS related Entries
    def deleteAASDataColumn(self):
        try:
            insertResult = self.AAS_Database_Server.delete_one("AASX")
            if (insertResult["message"] == "failure"):
                returnMessageDict = {"message" : ["The AASX Column deletion is not executed properly."], "status": 201}
            elif (insertResult["message"] == "success"):
                returnMessageDict = {"message" : ["The Asset Administration Shell Column was deleted successfully"], "status": 200}
            else:
                returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}            
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteAASDataColumn dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict
  
    def updateAASDataList(self):
        aasData = self.pyAAS.aasConfigurer.jsonData
        aasContentData = {}
        i = 0
        aasIdSet = set()
        for aasEntry in aasData["assetAdministrationShells"]:
            aasEData = {}
            submodels = []
            aasEData["idShort"] = aasEntry["idShort"]
            try: aasEData["description"]  = aasEntry["description"] 
            except: pass
            aasEData["identification"]  = aasEntry["identification"]
            for submodelRef in aasEntry["submodels"]:
                for aasSubmodel in aasData["submodels"]:
                    if submodelRef["keys"][0]["value"] == aasSubmodel["identification"]["id"]:
                        submodels.append(aasSubmodel)
                aasEData["submodels"] = submodels
            assets = []
            for assetRef in aasEntry["asset"]["keys"]:
                for aasAsset in aasData["assets"]:
                    try:
                        if assetRef["value"] == aasAsset["identification"]["id"]:
                            assets.append(aasAsset)
                    except Exception as E: self.pyAAS.serviceLogger.info("Error at updateAASDataList dbadaptor_Custom" + str(E))
                                              
                aasEData["assets"] = assets
            aasContentData[i] = aasEData
            i = i + 1
            aasIdSet.add(aasEntry["identification"]["id"])

        self.pyAAS.aasIdList.clear()
        for identificationId in aasIdSet:
            self.pyAAS.aasIdList.append((identificationId,0))
        self.pyAAS.aasContentData = aasContentData

    def updateAASDataColumn(self,aasData):
        try:
            insertResult = self.AAS_Database_Server.insert_one(self.col_AASX,aasData)
            if (insertResult["message"] == "failure"):
                returnMessageDict = {"message" : ["The AASX is not updated."], "status": 201}
            elif (insertResult["message"] == "success"):
                self.pyAAS.aasConfigurer.jsonData = aasData
                self.updateAASDataList()
                self.pyAAS.aasConfigurer.getStandardSubmodels()
                self.pyAAS.aasConfigurer.getAASList()
                try:
                    self.pyAAS.AASendPointHandlerObjects["MQTT"].restart()
                except Exception as E:
                    self.pyAAS.serviceLogger.info("Error at dbadaptor_Custom restarting MQTT adaptors" + str(E))
                returnMessageDict = {"message" : ["The AASX is updated successfully"], "status": 200}
            else:
                returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}
        except Exception as E: 
            self.pyAAS.serviceLogger.info("Error at updateAASDataColumn dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict
        
    def deleteUpdateAASXColumn(self,aasData,note):
        deleteResponse = self.deleteAASDataColumn()
        if (deleteResponse["status"] == 200):
            updateResponse = self.updateAASDataColumn(aasData)
            if (updateResponse["status"] == 200):
                returnMessageDict = {"message" : [note+" updated successfully"], "status": 200}
            elif (updateResponse["status"] == 201):
                returnMessageDict = {"message" : [note+" is not updated"], "status": 200}
            else:
                returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}    
        else:
            returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}
        return returnMessageDict  

    def postAASXEntity(self,data):
        try:
            entity = data["entity"]
            note = data["note"]
            entityData = data["updateData"]
            aasData = self.pyAAS.aasConfigurer.jsonData
            aasData[entity].append(entityData)
            updateResponse = self.deleteUpdateAASXColumn(aasData,note)
            return updateResponse
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAASXEntityByID dbadaptor_Custom" + str(E))
            return {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}

    def getEntityList(self,data):
        try:
            entity = data["entity"]
            note = data["note"]
            aasData = self.pyAAS.aasConfigurer.jsonData
            if (len(aasData[entity]) != 0): 
                entityList = {}
                i = 0
                for entityData in aasData[entity]:
                    entityList[i] = entityData
                    i = i + 1
                return {"message" : entityList, "status" : 200}
            else:
                return {"message" : [note + "are registered"], "status" : 200}
        except Exception as E:
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict

  
    def getAASXEntityById(self,data):
        returnMessageDict = {}
        entity = data["entity"]
        entityId = data["entityId"]
        note = data["note"]
        try:
            aasData = self.pyAAS.aasConfigurer.jsonData
            for eIter in aasData[entity]:
                if entityId == eIter["identification"]["id"]:
                    return {"message" : [eIter], "status" : 200}
            returnMessageDict = {"message":[note + " with the passed Id not found"],"status":200}
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASXEntityById dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict

    def deleteAASXEntityByID(self,data):
        entity = data["entity"]
        entityId = data["entityId"]
        note = data["note"]        
        try:
            aasData = self.pyAAS.aasConfigurer.jsonData
            i = 0
            for eIter in aasData[entity]:
                if entityId == eIter["identification"]["id"]:
                    del aasData[entity][i]
                    updateResponse = self.deleteUpdateAASXColumn(aasData,note)
                    if (updateResponse["status"] == 200):
                        return {"message":[note +" is deleted succesfully"],"status":200}
                    else:
                        return updateResponse
                i = i + 1
            returnMessageDict = {"message":[note +" with passed id found"],"status":200}
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteAASXEntityByID dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict

    def putAASXEntityByID(self,data):
        entity = data["entity"]
        entityId = data["entityId"]
        note = data["note"]
        entityData = data["entityData"]        
        try:
            deleteResponse = self.deleteAASXEntityByID(data)
            if (deleteResponse["status"] == 500):
                return deleteResponse
            else:
                aasData = self.pyAAS.aasConfigurer.jsonData
                aasData[entity].append(entityData)
                updateResponse = self.deleteUpdateAASXColumn(aasData,note)
                return updateResponse
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAASXEntityByID dbadaptor_Custom" + str(E))
            return {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}


    def getAASXEntityByIDSubEntityList(self,data):
        returnMessageDict = {}
        try:
            entity = data["entity"]
            entityId = data["entityId"]
            note = data["note"]
            subEntity = data["subEntity"]
            aasData = self.pyAAS.aasConfigurer.jsonData
            for eIter in aasData[entity]:
                if entityId == eIter["identification"]["id"]:
                    return {"message" : [eIter[entity][subEntity]], "status" : 200}
            returnMessageDict = {"message":[note + " with the passed Id not found"],"status":200}
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASXEntityById dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict    

    def postAASXEntityByIDSubEntityList(self,data):
        entity = data["entity"]
        entityId = data["entityId"]
        note = data["note"]
        subEntity = data["subEntity"]
        entityData = data["updateData"]
        returnMessageDict = {}
        try:
            aasData = self.pyAAS.aasConfigurer.jsonData
            for eIter in aasData[entity]:
                if entityId == eIter["identification"]["id"]:
                    aasData[entity][subEntity].append(entityData)
                    updateResponse = self.deleteUpdateAASXColumn(aasData,note)
                    return updateResponse
            returnMessageDict = {"message":[note + " with the passed Id not found"],"status":200}
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAASXEntityByIDSubEntityList dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict    

    def opSubmodelElementByIdShortPath(self,data):
        try:    
            entityId = data["entityId"]
            idShortPath = data["idShortPath"].split(".")
            aasData = self.pyAAS.aasConfigurer.jsonData
            indexPath = []
            for eIter in aasData["submodels"]:
                if entityId == eIter["identification"]["id"] or entityId == eIter["idShort"]:
                    i = 0
                    for submodelElem in eIter["submodelElements"]:
                        if submodelElem["idShort"] == idShortPath[0]:
                            indexPath.append(i)
                            return self._opSubmodelElementByIdShortPath(submodelElem,idShortPath[1:],data,indexPath,eIter)
                    i = i + 1
            return {"message": ["No submodel with the specified Id exists"],"status":200}
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at opSubmodelElementByIdShortPath dbadaptor_Custom" + str(E))   
            return {"message": ["Unexpected Internal Error"],"status":500}  
    
    def _updateSubmodelElem(self,subElem,indexPath,data):
        _opType =  data["opType"] 
        if (len(indexPath) == 1):
            if _opType == "post":
                subElem["value"].append(data["updateData"])
            elif _opType == "delete":
                del subElem["value"][indexPath[0]]
            elif _opType == "put":
                del subElem["value"][indexPath[0]]
                subElem["value"].insert(indexPath[0],data["updateData"])
        else: 
            subElem["value"][indexPath[0]] =  self._updateSubmodelElem(subElem["value"][indexPath[0]],indexPath[1:],data)
        return subElem
    
    def _opTypeSubmodelElementByIdShortPath(self,data,indexPath,submodel):
        if (len(indexPath) == 1):
            _opType =  data["opType"] 
            if _opType == "post":
                submodel["submodelElements"].append(data["updateData"])
            elif _opType == "delete":
                del submodel["submodelElements"][indexPath[0]]
            elif _opType == "put":
                del submodel["submodelElements"][indexPath[0]]
                submodel["value"].insert(data["updateData"],indexPath[0])
        else:
            submodel["submodelElements"][indexPath[0]] = self._updateSubmodelElem(submodel["submodelElements"][indexPath[0]],indexPath[1:],data)
        postData = {"entity":"submodels","entityId":data["entityId"],"note":data["note"]}
        postData["entityData"] = submodel
        return self.putAASXEntityByID(postData)
            
    def _opSubmodelElementByIdShortPath(self,submodelElement,idShortPath,data,indexPath,submodel):
        try:
            if (len(idShortPath) == 0):
                if (data["opType"] == "get"):
                    return {"message":[submodelElement],"status":200}
                if (data["opType"] == "post"):
                    return self._opTypeSubmodelElementByIdShortPath(data,indexPath,submodel)
                elif (data["opType"] == "put"):
                    return self._opTypeSubmodelElementByIdShortPath(data,indexPath,submodel)
                elif (data["opType"] == "delete"): 
                    return self._opTypeSubmodelElementByIdShortPath(data,indexPath,submodel)
            else:
                if (submodelElement["modelType"]["name"] == "SubmodelElementCollection"):
                    i = 0
                    for elem in submodelElement["value"]:
                        if (elem["idShort"] == idShortPath[0]):
                            indexPath.append(i)
                            return self._opSubmodelElementByIdShortPath(elem,idShortPath[1:],data,indexPath,submodel)
                        i = i + 1
                    return {"message":["The submodel element is not found"], "status" : 200}
                else :
                    if (submodelElement["idShort"] == idShortPath[0]):
                        return self._opSubmodelElementByIdShortPath(submodelElement,idShortPath[1:],data,indexPath,submodel)
                    else:
                        return {"message":["The submodel element is not found"], "status" : 200}
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at _opSubmodelElementByIdShortPath dbadaptor_Custom" + str(E))
            return {"message": ["Unexpected Internal Error"+str(E)],"status":500}

    def createNewConversation(self,coversationId):
        returnMessageDict = {}
        coversationId = coversationId
        newConversation = {
                "coversationId":coversationId, 
                "messages":   []
            }
        try:
            self.AAS_Database_Server.insert_one(self.col_Messages, newConversation)
            returnMessageDict = {"message": ["The details are successfully recorded"],"status":200}            
        except Exception as E:
            returnMessageDict = {"message": ["Unexpected Internal Error"],"status":500}
        return returnMessageDict 
                  
    def saveNewConversationMessage(self,coversationId,messageType,messageId,direction,message,entryTime):
        message = {
                    "messageType" : messageType,
                    "message_Id" : messageId,
                    "message" : message,
                    "direction" : direction,
                    "coversationId" : coversationId,
                    "entryTime": entryTime,
                }
        returnMessageDict = {}
        try:
            conversation = self.AAS_Database_Server.find(self.col_Messages,{ "$and": [ { "coversationId":coversationId }]})["data"]
            conversation["messages"].append(message)
            self.AAS_Database_Server.remove(self.col_Messages,{ "$or": [ { "coversationId":coversationId }]})
            self.AAS_Database_Server.insert_one(self.col_Messages, conversation)
            returnMessageDict = {"message": ["The details are successfully recorded"],"status":200}            
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at saveNewConversationMessage dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Error"],"status":500}
        return returnMessageDict    
    
    def getMessageCount(self):
        try:
            returnMessageDict = {"message": [self.AAS_Database_Server.dataCount(self.col_Messages)],"status":200}
        except:
            returnMessageDict = {"message": [0],"status":500}
        return returnMessageDict   

    def createOutnInboundInternal(self,resultList):
        returnData = {"inbound":[],"outbound":[],"internal":[]}
        for result in resultList["messages"]:
            if (result["direction"] == "inbound"):
                returnData["inbound"].append(result["message"]["frame"]["messageId"]+":"+result["entryTime"])
            elif(result["direction"] == "outbound"):
                returnData["outbound"].append(result["message"]["frame"]["messageId"]+":"+result["entryTime"])
            elif(result["direction"] == "internal"):
                returnData["internal"].append(result["message"]["frame"]["messageId"]+":"+result["entryTime"])                
        return returnData

    def getConversationsById(self,coversationId):
        returnMessageDict = {}
        try:
            conversation = self.AAS_Database_Server.find(self.col_Messages,{ "$and": [ { "coversationId":coversationId }]})["data"]
            returnMessageDict = {"message": self.createOutnInboundInternal(conversation),"status":200}            
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getConversationsById dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Error"],"status":500}
        return returnMessageDict

    def getMessagebyId(self,messageId,conversationId):
        returnMessageDict = {}
        try:
            messagesList = self.AAS_Database_Server.find(self.col_Messages,{ "$and": [ { "coversationId":conversationId }]})["data"]["messages"]
            for message in messagesList:
                data = message["message"]
                if messageId == message["message_Id"]:
                    if  ("submodelElements" in list(data.keys())):
                        i = 0
                        for iM in data["interactionElements"]:
                            if ("submodelElements" in list(iM.keys())):
                                data["interactionElements"][i] = self.getSubmodePropertyDict(iM)
                            elif ("assetAdministrationShells" in list(iM.keys())):
                                data["interactionElements"][i] = str(iM)
                            else:
                                data["interactionElements"][i] = iM
                            i = i + 1
                        returnMessageDict = {"message": [data],"status":200}
                    else:
                        returnMessageDict = {"message": [data],"status":200}
        except Exception as E:
            returnMessageDict = {"message": ["Unexpected Internal Error"],"status":500}
        return returnMessageDict

    def processEachSubmodelElement(self,submodelElement):
        if submodelElement["modelType"]["name"] == "SubmodelElementCollection":
            elemCollection = {}
            for elem in submodelElement["value"]:
                if elem["modelType"]["name"] == "SubmodelElementCollection":
                    elemCollection[elem["idShort"]] = self.processEachSubmodelElement(elem)
                else:
                    if (elem["modelType"]["name"] == "Property"):
                        elemCollection[elem["idShort"]] = elem["value"] 
                    elif (elem["modelType"]["name"] == "Range"):
                        elemCollection[elem["idShort"]] = {"min" :elem["min"] ,"max":elem["max"]}
                        
            return elemCollection
        else: 
            return submodelElement["value"]
    
    def getSubmodePropertyDict(self,submodel):
        submodelProperetyDict = {}
        for eachProperty in submodel["submodelElements"]:
            submodelProperetyDict[eachProperty["idShort"]] = self.processEachSubmodelElement(eachProperty)
        return submodelProperetyDict


## Message Level Entries


#### AASDescritpors Registry Start ######################

 
######### Submodel Registry API Services End ###############################


#AASsubmodel,AASsubmodelSubmodelElements,AASsubmodelSubmodelElementsValue,AASsubmodelSubmodelElementsByPath,AASsubmodelSubmodelElementsByPathValue
        
    def getAAsSubmodelbyIdSubmodelElem(self,data):
        submodelId = data["submodelId"]
        returnMessageDict = {}
        resultList = []
        resultListTemp = []
        try:
            aasSubmodels = self.getAAS(data)            
            for aas in aasSubmodels["message"]:
                for submodel in aas["submodels"]:
                    resultListTemp.append(submodel)

            if len(resultListTemp) == 0:
                returnMessageDict = {"message": ["No submodels are yet registered"],"status":500}
                
            else :
                for submodel in resultListTemp:
                    if submodel["idShort"] == submodelId or submodel["identification"]["id"] == submodelId :
                        for submodelElem in submodel["submodelElements"]:
                            resultListTemp.append(submodelElem)
                if len(resultList) == 0:
                    returnMessageDict = {"message": ["The AAS does not contain the specified submodel"],"status":500}
                else:
                    returnMessageDict = {"message": resultList,"status":200}
                
        except Exception as E:
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict 

    def modifyRaddQual(self,submodelElement,qualifier):
        if "constraints" in list(submodelElement.keys()):
            i = 0
            qualpresent = False
            for qual in submodelElement["constraints"]:
                if (qual["type"] == qualifier["type"]):
                    submodelElement["constraints"][i]["value"] = qualifier["value"]
                    qualpresent = True
                    break
            if (not qualpresent):
                submodelElement["constraints"].append(qualifier)        
        return submodelElement

    def _retrievenUpdateSubmodelElementQual(self,submodelElement,idShortPath,qualifier):
        if (len(idShortPath) == 0):
            return self.modifyRaddQual(submodelElement,qualifier)
        else:
            if (submodelElement["modelType"]["name"] == "SubmodelElementCollection"):
                i = 0
                for elem in submodelElement["value"]:
                    if (elem["idShort"] == idShortPath[0]):
                        submodelElement["value"][i] = self._retrievenUpdateSubmodelElementQual(elem,idShortPath[1:],qualifier)
                        break
                    i = i + 1
                return  submodelElement
            else:
                return self.modifyRaddQual(submodelElement,qualifier)
        
    def putSubmodelElementQualbyId(self,data):
        idShortPath = data["idShortPath"]
        if ("." in idShortPath):
            idShortPath = data["idShortPath"].split(".")
        else:
            idShortPath = [idShortPath]
        qualifier = data["updateData"]
        try:    
            returnResponse = self.getSubmodelById(data)
            if (returnResponse["status"] == 200):
                submodel =  returnResponse["message"][0]
                i = 0
                for submodelElem in submodel["submodelElements"]:
                    for _idShortPath in idShortPath:
                        if (submodelElem["idShort"] == idShortPath[0]):
                            submodel["submodelElements"][i] = self._retrievenUpdateSubmodelElementQual(submodelElem,idShortPath[1:],qualifier)
                            break
                    i = i + 1        
                return self.putSubmodelById({"updateData" :submodel,"submodelId":data["submodelId"]})
            else:
                return returnResponse
        except Exception as E:   
            return {"message": ["Unexpected Internal Error"+str(E)],"status":500}  
   
if __name__ == "__main__":
    dba = DB_ADAPTOR()
    dba.getAAS()