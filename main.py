import schemathesis
from hypothesis import settings
from schemathesis.checks import not_a_server_error, content_type_conformance, \
    response_schema_conformance

# load openapi specification from local file.
schema = schemathesis.from_path('open_api_specification_aas_v2.json')
print(schema)
schema.base_url = 'http://127.0.0.1:4001/aasServer/'


@schema.parametrize()
@settings(max_examples=20)
def test_api(case):
    case.call_and_validate(checks=(not_a_server_error, content_type_conformance, response_schema_conformance))
