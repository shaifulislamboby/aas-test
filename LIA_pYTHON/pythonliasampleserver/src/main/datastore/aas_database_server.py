'''
Copyright (c) 2021-2022 Otto-von-Guericke-Universiat Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

class AAS_Database_Server(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.AASRegistryDatabase = self.pyAAS.aasConfigurer.dataBaseFile
    
    def createNewDataBaseColumn(self,colName):
        if colName in self.AASRegistryDatabase:
            return colName
        else:
            self.AASRegistryDatabase[colName] =  []
            return colName
    
    def checkforExistenceofColumn(self,colName):
        if colName in self.AASRegistryDatabase:
            if self.AASRegistryDatabase[colName] == []:
                return "empty column"
            else:
                return "data present"
        else:
            return "column not present"
        
    def insert_one(self,colName,insertData):
        self.AASRegistryDatabase[colName].append(insertData)
        return self.pyAAS.aasConfigurer.saveToDatabase(self.AASRegistryDatabase,colName)

    def delete_one(self,colName):
        self.AASRegistryDatabase[colName] = []
        return self.pyAAS.aasConfigurer.saveToDatabase(self.AASRegistryDatabase,colName)   
    
    def find(self,colName,query):
        try:
            databaseColumn =  self.AASRegistryDatabase[colName]
            
            if "$or" in query:
                queryTerms = query["$or"]
                for databaseRow in databaseColumn:
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if ( queryTerm[key] == databaseRow[key] and queryTerm[key] != ""):
                                return {"data" :databaseRow, "message": "success"}
                return {"data":"Not found","message":"failure"}
            
            elif "$and" in query:
                queryTerms = query["$and"]
                checkLength = len(queryTerms)
                for databaseRow in databaseColumn:
                    i = 0
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if (queryTerm[key] ==  databaseRow[key] and queryTerm[key] != ""):
                                i = i + 1
                    if (i == checkLength):
                        return {"data" :databaseRow, "message": "success"}            
            elif len(query.keys()) == 0:
                if (len(databaseColumn) == 0):
                    return {"data":"Not found","message":"failure"}
                else:
                    return {"message":"success","data":databaseColumn}
            
            else:
                return {"data":"Not found","message":"failure"}
        except Exception as E:
            return {"data":"Not found","message":"error"}  

    def remove(self,colName,query):
        try:
            databaseColumn =  self.AASRegistryDatabase[colName]
            if "$or" in query:
                queryTerms = query["$or"]
                i = 0 
                for databaseRow in databaseColumn:
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if (queryTerm[key] == databaseRow[key]):
                                del self.AASRegistryDatabase[colName][i]
                                self.pyAAS.aasConfigurer.saveToDatabase(self.AASRegistryDatabase,"messages")
                                return { "message": "success","index":i}
                    i = i + 1
                return {"message":"failure","data":"error"}
            
            if "$and" in query:
                queryTerms = query["$and"]
                checkLength = len(queryTerms)
                k = 0
                for databaseRow in databaseColumn:
                    i = 0
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if (queryTerm[key] == databaseRow[key]):
                                i = i + 1
                    k = k + 1
                if (k == checkLength):
                        del self.AASRegistryDatabase[colName][i]
                        self.pyAAS.aasConfigurer.saveToDatabase(self.AASRegistryDatabase)
                        return {"message": "success","index":i}
                return {"message":"failure","data":"error"}    
        except Exception as E:
            print(str(E))
            return {"message":"error","data":"error"}        
    
    def dataCount(self,colName):
        return len(self.AASRegistryDatabase[colName])