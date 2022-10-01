import schemathesis

schema = schemathesis.from_path(
    'asset_administration_shells/aas_openapi_specifications/open_api_specification_aas_v2.json')

schema.base_url = 'http://localhost:8080'


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
