# import json
# import requests
# from jsonschema import validate
#
# # load openapi specification from local file.
# json_obj = json.load(open('aasTest/open_api_specification_aas_v2.json'))
#
# # schema = schemathesis.from_dict(json_obj)
# # schema = jsonref.loads(str(json.dumps(json_obj)))
# data = {
#     "modelType": {
#         "name": "AssetAdministrationShell"
#     },
#     "assetInformation": {
#         "assetKind": "Instance",
#         "globalAssetId": {
#             "keys": [
#                 {
#                     "idType": "Iri",
#                     "type": "Asset",
#                     "value": "https://acplt.org/Test_Asset"
#                 }
#             ]
#         },
#         "billOfMaterial": [
#             {
#                 "keys": [
#                     {
#                         "idType": "Iri",
#                         "type": "Submodel",
#                         "value": "http://acplt.org/Submodels/Assets/TestAsset/BillOfMaterial"
#                     }
#                 ]
#             }
#         ]
#     },
#     "submodels": [
#         {
#             "keys": [
#                 {
#                     "idType": "Iri",
#                     "type": "Submodel",
#                     "value": "https://example.com/ids/sm/1145_8090_6012_5097"
#                 }
#             ]
#         },
#         {
#             "keys": [
#                 {
#                     "idType": "Iri",
#                     "type": "Submodel",
#                     "value": "https://example.com/ids/sm/4445_8090_6012_7409"
#                 }
#             ]
#         },
#         {
#             "keys": [
#                 {
#                     "idType": "Iri",
#                     "type": "Submodel",
#                     "value": "https://example.com/ids/sm/2110_9090_6012_8448"
#                 }
#             ]
#         },
#         {
#             "keys": [
#                 {
#                     "idType": "Iri",
#                     "type": "Submodel",
#                     "value": "https://example.com/ids/sm/5410_9090_6012_0950"
#                 }
#             ]
#         },
#         {
#             "keys": [
#                 {
#                     "idType": "Iri",
#                     "type": "Submodel",
#                     "value": "https://example.com/ids/sm/2402_1191_1022_1090"
#                 }
#             ]
#         }
#     ],
#     "identification": {
#         "idType": "Iri",
#         "id": "https://example.com/ids/aas/3235_8090_6012_8930"
#     },
#     "idShort": "FestoDemoAAS"
# }
# base_url = 'http://0.0.0.0:8080'
# success = []
# for paths, value in json_obj.get('paths').items():
#     if '{' not in paths:
#         response = None
#         url = paths
#         for val in value:
#             if val == 'get':
#                 try:
#                     response = requests.get(url=f'{base_url}{url}').json()[0]
#                     validate(response, schema=json_obj)
#                     success.append(url)
#                 except Exception as error:
#                     print(error)
#
#                 print(response)
#                 print(url)
#         if response and val in ('post', 'put', 'patch'):
#             post_response = requests.post(url=f'{base_url}{url}', json=response)
#             print(f'post --- >{post_response.status_code} {post_response.json()}')
#
# print(success)
import json
from dataclasses import dataclass

import requests
from aas import examples, model

print(examples)

identifier = model.Identifier('https://acplt.org/Simple_Submodel', model.IdentifierType.IRI)
submodel = model.Operation(id_short='sas').__dict__
submodel.pop('_kind')
submodel.pop('qualifier')
print(
    submodel
)
response = requests.post(
    'http://localhost:8080/shells/aHR0cHM6Ly9leGFtcGxlLmNvbS9pZHMvYWFzLzMyMzVfODA5MF82MDEyXzg5MzI=/'
    'aas/submodels/aHR0cHM6Ly9leGFtcGxlLmNvbS9pZHMvc20vMjQwMl8xMTkxXzEwMjJfMTA5MA==/submodel/submodel-elements'
    '/ProcessDuration/invoke/',
    json={
        "modelType": {
            "name": "Property"
        },
        "kind": "Instance",
        "semanticId": {
            "keys": [
                {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-BAA120#008",
                    "idType": "IRDI"
                }
            ]
        },
        "idShort": "ProcessDuration",
        "category": "PARAMETER",
        "value": "5000",
        "valueType": "integer"
    })
# {
#     "description": "switches light on if state is set to True, off if state is False, returns true if operation "
#                    "successful",
#     "parameters": {
#         "state": {
#             "type": "boolean"
#         }
#     }})

print(response.status_code)
print(response.json())


@dataclass
class Base:

    @property
    def raw_value(self):
        return 99

    @property
    def mode_type(self):
        return self.raw_value

    @property
    def id_type(self):
        return self.raw_value


@dataclass
class SubModel(Base):
    raw_sub_model: dict

    @property
    def kind(self):
        return self.raw_sub_model.get('kind')

    @property
    def semantic_id(self):
        return self.raw_sub_model.get('semanticId')


base = Base()

print(base.id_type)