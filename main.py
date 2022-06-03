import schemathesis


# load openapi specification from local file.
schema = schemathesis.from_path('open_api_specification_aas_v2.json')


@schema.parametrize()
def test_api(case):
    case.call_and_validate()