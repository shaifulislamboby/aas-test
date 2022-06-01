import schemathesis

schema = schemathesis.from_uri("https://example.schemathesis.io/openapi.json")


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
