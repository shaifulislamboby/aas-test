import schemathesis
import hypothesis.strategies as st
from dataclasses import dataclass

schema = schemathesis.from_uri("http://127.0.0.1:8000/api/schema/")


@schema.parametrize()
def test_api(case):
    case.call_and_validate()


@dataclass
class TestGET:
    """
    This is an example of initial test class,
    we can make our test class like this.
    """
    schema: dict
    errors: dict

    @st.lists
    def test_case_one(self):
        assert not 500
        pass

    @st.lists
    def test_case_two(self):
        # assert response conform to schema
        pass

    @st.lists
    def test_required_fields_are_available(self):
        pass

    def run_all_tests(self):
        self.test_case_one()
        self.test_case_two()
        return self.errors



