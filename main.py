import json
import requests
from jsonschema import validate

# load openapi specification from local file.
json_obj = json.load(open('open_api_specification_aas_v2.json'))

# schema = schemathesis.from_dict(json_obj)
# schema = jsonref.loads(str(json.dumps(json_obj)))
data = {
    "modelType": {
        "name": "AssetAdministrationShell"
    },
    "assetInformation": {
        "assetKind": "Instance",
        "globalAssetId": {
            "keys": [
                {
                    "idType": "Iri",
                    "type": "Asset",
                    "value": "https://acplt.org/Test_Asset"
                }
            ]
        },
        "billOfMaterial": [
            {
                "keys": [
                    {
                        "idType": "Iri",
                        "type": "Submodel",
                        "value": "http://acplt.org/Submodels/Assets/TestAsset/BillOfMaterial"
                    }
                ]
            }
        ]
    },
    "submodels": [
        {
            "keys": [
                {
                    "idType": "Iri",
                    "type": "Submodel",
                    "value": "https://example.com/ids/sm/1145_8090_6012_5097"
                }
            ]
        },
        {
            "keys": [
                {
                    "idType": "Iri",
                    "type": "Submodel",
                    "value": "https://example.com/ids/sm/4445_8090_6012_7409"
                }
            ]
        },
        {
            "keys": [
                {
                    "idType": "Iri",
                    "type": "Submodel",
                    "value": "https://example.com/ids/sm/2110_9090_6012_8448"
                }
            ]
        },
        {
            "keys": [
                {
                    "idType": "Iri",
                    "type": "Submodel",
                    "value": "https://example.com/ids/sm/5410_9090_6012_0950"
                }
            ]
        },
        {
            "keys": [
                {
                    "idType": "Iri",
                    "type": "Submodel",
                    "value": "https://example.com/ids/sm/2402_1191_1022_1090"
                }
            ]
        }
    ],
    "identification": {
        "idType": "Iri",
        "id": "https://example.com/ids/aas/3235_8090_6012_8930"
    },
    "idShort": "FestoDemoAAS"
}
base_url = 'http://0.0.0.0:8080'
success = []
for paths, value in json_obj.get('paths').items():
    if '{' not in paths:
        response = None
        url = paths
        for val in value:
            if val == 'get':
                try:
                    response = requests.get(url=f'{base_url}{url}').json()[0]
                    validate(response, schema=json_obj)
                    success.append(url)
                except Exception as error:
                    print(error)

                print(response)
                print(url)
        if response and val in ('post', 'put', 'patch'):
            post_response = requests.post(url=f'{base_url}{url}', json=response)
            print(f'post --- >{post_response.status_code} {post_response.json()}')

print(success)

