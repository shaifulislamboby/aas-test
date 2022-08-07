import schemathesis
from hypothesis import settings, given
from schemathesis.checks import not_a_server_error, content_type_conformance, \
    response_schema_conformance

# load openapi specification from local file.
schema = schemathesis.from_path('open_api_specification_aas_v2.json')
# print(schema)
# schema.base_url = 'http://127.0.0.1:5080/'


# @schema.parametrize()
# @settings(max_examples=20)
# def test_api(case):
#     case.call_and_validate(checks=())


data = {
          "description": "Reference to the Submodel",
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Reference"
              }
            }
          },
          "required": True
        }

from hypothesis_jsonschema import from_schema
import json
import jsonref

json_obj = json.load(open('open_api_specification_aas_v2.json'))
schema = jsonref.loads(str(json.dumps(json_obj)))
data = schema.get('paths').get('/concept-descriptions/{cdIdentifier}').get('put').get('requestBody').get('content').get('application/json').get('schema')

@given(from_schema(data))
def test(value):
    x = value
    print(value)
