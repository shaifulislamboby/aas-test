import schemathesis

schema = schemathesis.from_uri("http://127.0.0.1:8000/api/schema/")


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
