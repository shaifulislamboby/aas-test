'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
from flask_restful import Resource,request
from flask import render_template,Response,redirect,flash,make_response,session,send_file,send_from_directory
from requests.utils import unquote
import uuid
try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic

try:
    from utils.utils import ExecuteDBModifier,ProductionStepOrder,SubmodelUpdate,SubmodelElement,ExecuteDBRetriever,AASMetaModelValidator
except ImportError:
    from main.utils.utils import ExecuteDBModifier,ProductionStepOrder,SubmodelUpdate,SubmodelElement,ExecuteDBRetriever,AASMetaModelValidator
import os

#AAS,AASSubmodelELements,AASSubmodelELement,AASSubmodelReferences,AASSubmodel,AASAssetInformation,ConceptDescriptions,ConceptDescription,Submodels,Submodel,SubmodelELement

class AssetAdministrationShells(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"assetAdministrationShells","note" : "No Asset Administration shells"},"method":"getEntityList"})            
            return make_response(dataBaseResponse["message"],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"data":{"updateData":data,
                                                          "entity" :"assetAdministrationShells","note" : "No Asset Administration shells"},"method":"postAASXEntity"})
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class ConceptDescriptions(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData",
                                            "entity" :"conceptDescriptions","note" : "No Concept Descriptions"},"method":"getEntityList"})            
            return make_response(dataBaseResponse["message"],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getConceptDescriptions Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"data":{"updateData":data,
                                                        "entity" :"conceptDescriptions","note" : "Concept Descriptions"},"method":"postAASXEntity"})
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postConceptDescriptions Rest" + str(E))
            return make_response("Internal Server Error",500)

class Submodels(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData",
                                            "entity" :"submodels","note" : "No Submodel"},"method":"getEntityList"})            
            return make_response(dataBaseResponse["message"],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodels Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"data":{"updateData":data,
                                                        "entity" :"submodels","note" : "Submodel"},"method":"postAASXEntity"})
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodels Rest" + str(E))
            return make_response("Internal Server Error",500)


class AssetAdministrationShell(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = unquote(aasIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData",
                                                     "entity":"assetAdministrationShells","entityId" :aasIdentifier,"note":"Asset Administration SHell"
                                                     },"method":"getAASXEntityById"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShell Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,aasIdentifier):
        try:
            data = request.json
            aasIdentifier = unquote(aasIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    if (aasIdentifier == data["identification"]["id"] or aasIdentifier == ["idShort"]):
                        edm = ExecuteDBModifier(self.pyAAS)
                        dataBaseResponse = edm.executeModifer({"entity":"assetAdministrationShells",
                                                               "entityId":aasIdentifier,
                                                                "entityData":data, 
                                                                "note":"Asset Administration Shell","method":"putAASXEntityByID"})
                        return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                    else:
                        return make_response("The aas-identifier in the uri and in AAS Shell do not match",200)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShell Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,aasIdentifier):
        try:
            aasIdentifier = unquote(aasIdentifier)
            edm = ExecuteDBModifier(self.pyAAS)
            dataBaseResponse = edm.executeModifer({"entity":"assetAdministrationShells",
                                                               "entityId":aasIdentifier,
                                                                "entityData":"", 
                                                                "note":"Asset Administration Shell","method":"deleteAASXEntityByID"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteAssetAdministrationShell Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

class ConceptDescription(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,cdIdentifier):
        try:
            cdIdentifier = unquote(cdIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData",
                                                     "entity":"conceptDescriptions","entityId" :cdIdentifier,"note":"Concept Description"
                                                     },"method":"getAASXEntityById"})  
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getConceptionDescription Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,cdIdentifier):
        try:
            data = request.json
            cdIdentifier = unquote(cdIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"entity":"conceptDescriptions",
                                                               "entityId":cdIdentifier,
                                                                "entityData":data, 
                                                                "note":"Concept Descriptions","method":"putAASXEntityByID"})
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putConceptionDescription Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,cdIdentifier):
        try:
            cdIdentifier = unquote(cdIdentifier)
            edm = ExecuteDBModifier(self.pyAAS)
            dataBaseResponse = edm.executeModifer({"entity":"conceptDescriptions",
                                                            "entityId":cdIdentifier,
                                                            "entityData":"", 
                                                            "note":"Concept Descriptionl","method":"deleteAASXEntityByID"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteConceptionDescription Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
 
class Submodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,submodelIdentifier):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData",
                                                     "entity":"submodels","entityId" :submodelIdentifier,"note":"Concept Description"
                                                     },"method":"getAASXEntityById"})  
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getConceptionDescription Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,submodelIdentifier):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"entity":"submodels",
                                                               "entityId":submodelIdentifier,
                                                                "entityData":data, 
                                                                "note":"Submodel","method":"putAASXEntityByID"})
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)


class AssetAdministrationShellsSubmodelRefs(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"assetAdministrationShells",
                                            "subEntity" : "submodels",
                                            "note" : "No Asset Administration shells"
                                            },"method":"getAASXEntityByIDSubEntityList"})            
            return make_response(dataBaseResponse["message"],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShellSubmodelRef(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"assetAdministrationShells",
                                            "subEntity" : "submodels",
                                            "note" : "No Asset Administration shells"
                                            },"method":"postAASXEntityByIDSubEntityList"})                      
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Asset Administration Shell Submodel Reference is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelELements(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "note" : "No Sumodel"
                                            },"method":"getAASXEntityByIDSubEntityList"})            
            return make_response(dataBaseResponse["message"],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodelELements Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "note" : "No Sumodel"
                                            },"method":"postAASXEntityByIDSubEntityList"})                      
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed SubmodelElement is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodelELements Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelElementByIdShortPath(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "idShortPath" : idShortPath,
                                            "submodelIdentifier" : submodelIdentifier,
                                            "note" : "No Sumodel",
                                            "opType": "get"
                                            },"method":"opSubmodelElementByIdShortPath","instanceId" : str(uuid.uuid1())})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

    def put(self,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"data":{"updateData":data, 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "idShortPath" : idShortPath,
                                            "submodelIdentifier" : submodelIdentifier,
                                            "note" : "No Sumodel",
                                            "opType": "put"
                                            },"method":"opSubmodelElementByIdShortPath","instanceId" : str(uuid.uuid1())}) 
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"data":{"updateData":data, 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "idShortPath" : idShortPath,
                                            "submodelIdentifier" : submodelIdentifier,
                                            "note" : "No Sumodel",
                                            "opType": "post"
                                            },"method":"opSubmodelElementByIdShortPath","instanceId" : str(uuid.uuid1())}) 
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)        


    def delete(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyAAS)
            dataBaseResponse = edm.executeModifer({"data":{"updateData":"emptyData", 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "idShortPath" : idShortPath,
                                            "submodelIdentifier" : submodelIdentifier,
                                            "note" : "No Sumodel",
                                            "opType": "delete"
                                            },"method":"opSubmodelElementByIdShortPath","instanceId" : str(uuid.uuid1())})             
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)    

class AASStaticSource(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,filename):      
        try:
            return send_from_directory(self.pyAAS.downlaod_repository,filename)
        except Exception as E:
            print(str(E))        

class AASStaticWebSources(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,type,filename):      
        try:
            if (type == "js"):
                return send_from_directory(self.pyAAS.js_repository,filename) 
            elif (type == "css"):
                return send_from_directory(self.pyAAS.css_repository,filename) 
            elif (type == "images"):
                return send_from_directory(self.pyAAS.img_repository,filename)            
        except Exception as E:
            print(str(E)) 
            
class AASassetInformation(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData"},"method":"getAssetInformation"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except:
            return make_response("Unexpected Internal Server Error",500)

class AASassetInformationById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,assetId):
        try:
            assetId = unquote(assetId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData","assetId":assetId},"method":"getAASaasetInformationById"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except:
            return make_response("Unexpected Internal Server Error",500)
    
    def put(self,assetId):
        try:
            assetId = unquote(assetId)
            data = request.json
            if "interactionElements" in data: 
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateAsset(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    dataBaseResponse = edm.executeModifer({"data":{"updateData":data,"assetId":assetId},"method":"putAASaasetInformationById","instanceId" : str(uuid.uuid1())})
                    return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            return make_response("Internal Server Error",500)

    def delete(self,aasetId):
        try:
            assetId = unquote(aasetId)
            edm = ExecuteDBModifier(self.pyAAS)
            dataBaseResponse = edm.executeModifer({"data":{"updateData":"empty","assetId":assetId},"method":"deleteAASaasetInformationById","instanceId" : str(uuid.uuid1())})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)

class AASsubmodelRefs(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasId):
        try:
            aasId = unquote(aasId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData","aasId": aasId},"method":"getSubmodelRefsByAASId"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except:
            return make_response("Unexpected Internal Server Error",500)

class AASsubmodelRefsIndentifier(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasId,submodelId):
        try:
            aasId = unquote(aasId)
            submodelId = unquote(submodelId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData","aasId": aasId,"submodelId":submodelId},"method":"getSubmodelRefsByIDByAASId"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except:
            return make_response("Unexpected Internal Server Error",500)
      
    def put(self,aasId,submodelId):
        try:
            aasId = unquote(aasId)
            submodelId = unquote(submodelId)
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else:
                if(True):
                    if (True):
                        edm = ExecuteDBModifier(self.pyAAS)
                        dataBaseResponse = edm.executeModifer({"data":{"updateData":{"submodels":[data]},"aasId":aasId,"submodelId":submodelId},"method":"putSubmodelRefbyIdByAASId","instanceId" : str(uuid.uuid1())})            
                        return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                    else:
                        return make_response("The namspace SubmodelId value and the IdShort value do not match",500)
                else:
                    return make_response("The syntax of the passed submodel data is not valid or malformed request",400)
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)

    def delete(self,aasId,submodelId):
        try:
            aasId = unquote(aasId)
            submodelId = unquote(submodelId)
            edm = ExecuteDBModifier(self.pyAAS)
            dataBaseResponse = edm.executeModifer({"data":{"updateData":"empty","aasId":aasId,"submodelId":submodelId},"method":"deleteSubmodelRefbyIdByAASId","instanceId" : str(uuid.uuid1())})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)
#


class SubmodelsById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,submodelId):
        try:
            submodelId = unquote(submodelId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData","submodelId":submodelId},"method":"getSubmodelById"})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except:
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,submodelId):
        try:
            aasValid = AASMetaModelValidator(self.pyAAS)
            submodelId = unquote(submodelId)
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else:
                if(aasValid.valitdateSubmodel({"submodels":[data]})):
                    if (True):
                        edm = ExecuteDBModifier(self.pyAAS)
                        dataBaseResponse = edm.executeModifer({"data":{"updateData":{"submodels":[data]},"submodelId":submodelId},"method":"putSubmodelById"})            
                        return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
                    else:
                        return make_response("The namspace SubmodelId value and the IdShort value do not match",500)
                else:
                    return make_response("The syntax of the passed submodel data is not valid or malformed request",400)
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)

    def delete(self,submodelId):
        try:
            edm = ExecuteDBModifier(self.pyAAS)
            submodelId = unquote(submodelId)
            dataBaseResponse = edm.executeModifer({"data":{"updateData":"empty","submodelId":submodelId},"method":"deleteSubmodelById","instanceId" : str(uuid.uuid1())})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)

class SubmodelElemsById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,submodelId):
        try:
            submodelId = unquote(submodelId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData","submodelId": submodelId},"method":"getSubmodeByIdlElements","instanceId" : str(uuid.uuid1())})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)



class SubmodelElementsByPathValue(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,submodelId,idShortPath):
        try:
            submodelId = unquote(submodelId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData","submodelId":submodelId,"idShortPath":idShortPath},"method":"getSubmodelByIdElementByIdShortPathValue","instanceId" : str(uuid.uuid1())})            
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            return make_response("Unexpected Internal Server Error",500)

    def put(self,submodelId,idShortPath):
        try:
            data = request.json
            submodelId = unquote(submodelId)
            edm = ExecuteDBModifier(self.pyAAS)
            dataBaseResponse = edm.executeModifer({"data":{"updateData":data,"submodelId":submodelId,"idShortPath":idShortPath},"method":"putSubmodelByIdElementByIdShortPathValue","instanceId" : str(uuid.uuid1())})
            return make_response(dataBaseResponse["message"][0],dataBaseResponse["status"])
        except Exception as E:
            return make_response("Internal Server Error",500)

class RetrieveMessage(Resource):    
    def __init__(self, pyAAS):
        self.pyAAS = pyAAS
        
    def post(self):
        jsonMessage = request.json
        try:
            if (jsonMessage["frame"]["sender"]["identification"]["id"] == self.pyAAS.AASID):
                pass
            else:
                self.pyAAS.msgHandler.putIbMessage(jsonMessage)
        except:
            pass

class AASWebInterfaceHome(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self):
        if not session.get('logged_in'):
            return redirect("/login")
        else:              
            try:
                return  Response(render_template('home.html',exDomain=self.pyAAS.exDomain ,aasList = self.pyAAS.AASData))
            except Exception as E:
                return str(E)

class AASWebInterface(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex):
        if not session.get('logged_in'):
            return redirect("/login")
        else:              
            try:
                return  Response(render_template('index.html',aasIndex=aasIndex, exDomain=self.pyAAS.exDomain , 
                                                        skillList= self.pyAAS.skillListWeb[aasIndex],
                                                        stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                        aasIdShort = self.pyAAS.aasContentData[aasIndex]["idShort"]))
            except Exception as E:
                return str(E)

class AASWebInterfaceStandardSubmodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.standardSubmodelWebPageDict = {"NAMEPLATE" : "nameplate.html", "DOCUMENTATION" : "documentation.html" ,
                                            "TECHNICAL_DATA" : "technicaldata.html" , "IDENTIFICATION": "identification.html", 
                                            "THING_DESCRIPTION" : "rtdata.html"}
    def get(self,aasIndex,stdsubmodelType):
        if not session.get('logged_in'):
            return redirect("/login")
        else:              
            try:
                return  Response(render_template(self.standardSubmodelWebPageDict[stdsubmodelType],
                                                 aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasContentData[aasIndex]["idShort"],
                                                 stdSubmodelData = self.pyAAS.aasStandardSubmodelData[aasIndex][stdsubmodelType]))
            except Exception as E:
                return str(E)    

class AASWebInterfaceSKillLog(Resource):
    
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex,skillName):
        if not session.get('logged_in'):
            return redirect("/login")
        else:           
            return  Response(render_template('skill.html',
                                             aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                             skillList= self.pyAAS.skillListWeb[aasIndex],
                                             stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                             skillName = skillName))

    def post(self,aasIndex,skillName):
        try:
            return self.pyAAS.skilllogListDict[aasIndex][unquote(skillName)].getCotent()
        except Exception as E:
            return str(E)

class AASWebInterfaceSubmodels(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex):
        if not session.get('logged_in'):
            return redirect("/login")
        else:          
            try:
                propertyListDict=(self.pyAAS.getSubmodelPropertyListDict(aasIndex))
                return  Response(render_template('submodels.html',
                                                 aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasContentData[aasIndex]["idShort"],propertyListDict=propertyListDict ))
            except Exception as e:
                return str(e)


class AASWebInterfaceSearch(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def post(self,aasIndex):
        try:
            updateInfo = request.form
            query =  updateInfo["searchQuery"]
            message1 = self.pyAAS.dba.getConversationsById(query)
            if message1["status"] == 200:
                messages = message1["message"]
                return  Response(render_template('search.html',
                                                  aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasContentData[aasIndex]["idShort"],
                                                 resultList = {query:messages}))
            else:
                count = self.pyAAS.dba.getMessageCount()
                flash("The conversation Id is not found, the last count is " + str(count["message"][0]),"error")
                return redirect("/"+str(aasIndex)+"/home")
                
        except Exception as e:
            flash("Error","error")
            return redirect("/"+str(aasIndex)+"/home")


class AASWebInterfaceConversationMessage(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIndex,query):
        if not session.get('logged_in'):
            return redirect("/login")
        else:          
            try:
                queryList = str(unquote(query)).split("**")
                return self.pyAAS.dba.getMessagebyId(queryList[0],queryList[1])["message"][0]
            except Exception as e:
                print(str(queryList) + str(e))
                return str(queryList) + str(e)

class AASWebInterfaceProductionManagement(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex):   
        if not session.get('logged_in'):
            return redirect("/login")
        else:          
            try:
                productionSequenceList =  []
                if (aasIndex in self.pyAAS.productionSequenceList):
                    productionSequenceList = self.pyAAS.productionSequenceList[aasIndex]
                else:
                    self.pyAAS.productionSequenceList[aasIndex] = []
                return Response(render_template('productionmanager.html',
                                                aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasContentData[aasIndex]["idShort"],
                                                productionStepList=self.pyAAS.productionStepList[aasIndex],
                                                conversationIdList=self.pyAAS.conversationIdList,productionSequenceList=productionSequenceList))
            except Exception as e:
                return str(e)

    def post(self,aasIndex):
        updateInfo = request.form
        tag =  updateInfo["operationType"]   
        
        if (tag =="home"):
            return redirect("/"+str(aasIndex)+"/productionmanager")
        
        elif (tag == "create"):
            productionStep = request.form.get("productionStep")
            self.pyAAS.productionSequenceList[aasIndex].append(productionStep)
            flash("New Production step is added","success")
            return redirect("/"+str(aasIndex)+"/productionmanager")
        
        elif (tag == "delete"):
            self.pyAAS.productionSequenceList[aasIndex] = []
            flash("New Production step is added","success")
            return redirect("/"+str(aasIndex)+"/productionmanager")
        
        elif (tag == "start"):
            try:
                pso = ProductionStepOrder(self.pyAAS)
                conversationID = pso.createProductionStepOrder(aasIndex)
                flash("New Order booked with Order ID " + conversationID + " is booked","info")
                return redirect("/"+str(aasIndex)+"/productionmanager")   
            except  Exception as e:
                flash("Error creating the conversation Id.","error")
                return redirect("/"+str(aasIndex)+"/productionmanager")


            
class AASWebInterfaceSkill(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIndex,skillName):
        if not session.get('logged_in'):
            return redirect("/login")
        else:           
            return  Response(render_template('skill.html',
                                             aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                             skillList= self.pyAAS.skillListWeb[aasIndex],
                                             stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                             skillName = skillName))

    def post(self,aasIndex):
        try:
            updateInfo = request.form
            self.pyAAS.serviceLogger.info(updateInfo)
            methodType = updateInfo["methodType"]
            submodelName = updateInfo["submodelName"]
            if methodType == "modify" :
                propertyName = updateInfo["propertyName"]
                newValue = updateInfo["newValue"]
                if newValue != "":
                    sUpdate = SubmodelUpdate(self.pyAAS)
                    modifyResponse = sUpdate.modify(submodelName,propertyName,newValue)
                    if (modifyResponse["status"] == 500):
                        flash("Internal Data Error","error")
                        return redirect("submodels")
                    else:
                        flash("Data updated succesfully","info")
                        return redirect("submodels")
                else:
                    flash("Empty data field cannot be updated","error")
                    return redirect("submodels")
                
            elif (methodType == "delete"):
                propertyName = updateInfo["propertyName"]
                sUpdate = SubmodelUpdate(self.pyAAS)
                modifyResponse = sUpdate.delete(propertyName,submodelName)
                if (modifyResponse["status"] == 500):
                    flash("Internal Data Error","error")
                    return redirect("submodels")
                else:
                    flash("Data updated succesfully","info")
                    return redirect("submodels")
        except Exception as e:
            flash(str(e),"error")
            return redirect("submodels")

class AASWebInterfaceSubmodelProperty(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def post(self):
        try:
            updateInfo = request.form
            IdShort =  updateInfo["IdShort"]
            Value = updateInfo["Value"]
            SemanticId = updateInfo["SemanticId"]
            submodelId = updateInfo["property"]
            
            if (IdShort == "" or Value == "" or  SemanticId == ""):
                flash("Please fill all the fields","error")
                return redirect("/submodels")
            else:
                submodeElement = SubmodelElement(IdShort,Value,SemanticId,self.pyAAS)
                submodelElem = submodeElement.create()
                returnmessage = submodeElement.addSubmodelElement(submodelElem,submodelId)
                if (returnmessage["status"] == 200):
                    subUpdate = SubmodelUpdate(self.pyAAS)
                    returnMessage = subUpdate.update(returnmessage["message"],submodelId)
                    print(returnMessage)
                    if (returnMessage["status"] == 200):
                        flash("Details updated Succesfully"+returnMessage["message"][0],"success")
                        return redirect("/submodels")
                    else:
                        flash("Internal error"+returnMessage["message"][0],"error")
                        return redirect("/submodels")
                else:
                    flash("Internal error"+returnMessage["message"][0],"error")
                    return redirect("/submodels")
        except Exception as E:
            return str(E)
      

class AASWebInterfaceLog(Resource):
    
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self):
        if not session.get('logged_in'):
            return redirect("/login")
        else:          
            return  Response(render_template('systemlog.html',exDomain=self.pyAAS.exDomain ,namePlateData = self.pyAAS.namePlateData,skillList= self.pyAAS.skillListWeb))

    def post (self):
        return self.pyAAS.ServiceLogList.getCotent()

class AASWebInterfaceRegister(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def post(self,aasIdentifier):
        try:
            updateInfo = request.form
            tabType = updateInfo["tabType"]
            if (tabType == "status"):
                try:
                    return redirect("register")
                except Exception as e:
                    flash("Error" + str(e),"info")
                    return redirect("register")
        except Exception as e:
            return self.pyAAS.msgHandler.RegisterLogList.getCotent()
    

    def get(self,aasIdentifier):
        if not session.get('logged_in'):
            return redirect("/login")
        else:          
            return  Response(render_template('register.html',aasId=aasIdentifier,exDomain=self.pyAAS.exDomain,namePlateData = self.pyAAS.namePlateData[aasIdentifier],skillList= self.pyAAS.skillListWeb[aasIdentifier],aasIdShort = self.pyAAS.aasContentData[aasIdentifier]["idShort"]))

class AASWebInterfaceSubmodelElemValue(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def getRelevantElemData(self,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,submodelELemType):
        edbR = ExecuteDBRetriever(self.pyAAS)
        dataBaseResponse = edbR.execute({"data":{"updateData":"emptyData", 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "idShortPath" : idShortPath,
                                            "entityId" : submodelName,
                                            "note" : "No Sumodel",
                                            "opType": "get"
                                            },"method":"opSubmodelElementByIdShortPath","instanceId" : str(uuid.uuid1())})            
        elemData = dataBaseResponse["message"][0]
        
        if (submodelELemType == "Property"):
            elemData["value"] = updateValue
        elif (submodelELemType == "Range"):
            elemData[submodelElemAdditionalInfo] = updateValue
        return elemData
    
    def performDBUpdate(self,updateValue,submodelELemType,submodelName,idShortPath,submodelElemAdditionalInfo):
        try:
            edm = ExecuteDBModifier(self.pyAAS)
            elemData = self.getRelevantElemData(updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,
                                                submodelELemType)
            edm.executeModifer({"data":{"updateData":elemData, 
                                            "entity" :"submodels",
                                            "subEntity" : "submodelElements",
                                            "idShortPath" : idShortPath,
                                            "entityId" : submodelName,
                                            "note" : "No Sumodel",
                                            "opType": "put"
                                            },"method":"opSubmodelElementByIdShortPath","instanceId" : str(uuid.uuid1())})          
        except Exception as E:
            print(str(E)) 

    def post(self,aasIndex):
        try:    
            updateData = request.form
            submodelName = updateData["submodelName"]
            submodelELemType = updateData["submodelElemType"]
            idShortPath = updateData["submodelElemidShortPath"]
            updateValue = updateData["newValue"]
            submodelElemAdditionalInfo = updateData["submodelElemAdditionalInfo"]
            self.performDBUpdate(updateValue,submodelELemType,submodelName,idShortPath,submodelElemAdditionalInfo)
            return redirect("/"+str(aasIndex)+"/submodels")
        except Exception as E:
            print(str(E))
            return redirect("/"+str(aasIndex)+"/submodels")
        
class AASDocumentationDownloadSubmodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasId,filename):
        try:
            file_path = os.path.join(self.pyAAS.downlaod_repository,filename)
            sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True)
            return  sendfile
        except Exception as E:
            print(str(E))

class AASDocumentationDownload(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,filename):
        try:
            file_path = os.path.join(self.pyAAS.downlaod_repository,filename)
            sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= "application/pdf")
            return  sendfile
        except Exception as E:
            print(str(E))

class AASRTDataVisualizer(Resource):        
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasId):
        if not session.get('logged_in'):
            return redirect("/login")
        else:          
            return  Response(render_template('rtdata.html',aasId=aasId,exDomain=self.pyAAS.exDomain ,tdProperties = self.pyAAS.tdProperties[aasId],skillList= self.pyAAS.skillListWeb[aasId],aasIdShort = self.pyAAS.aasContentData[aasId]["idShort"]))
    
    def post(self,aasId):
        returnData = {}
        try:
            for key in self.pyAAS.tdPropertiesList: 
                tdProperty = self.pyAAS.tdPropertiesList[key]
                if (tdProperty["aasIndex"] == aasId):
                    returnData[tdProperty["propertyName"]] = {'label': tdProperty["label"], 'value': tdProperty["value"]}
            return returnData
        except Exception as E:
            print(E)
            return {}
     