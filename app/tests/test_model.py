import datetime
import json
import unittest
from typing import Any
from unittest.mock import patch

from hypothesis import given, settings, strategies as st
from pydantic_factories import ModelFactory, Use

from data_definitions.numedy import InputPackage, InputModel, ProtoDatum
from model import Model
from method import ModelMethod


@st.composite
def build_correct_input_package(draw):
    class DatumFactory(ModelFactory[Any]):
        __model__ = ProtoDatum
        measure_time = datetime.datetime.now()

    class InputModelFactory(ModelFactory[Any]):
        __model__ = InputModel

        create_time = datetime.datetime.now()
        gender_id = draw(st.integers(min_value=0, max_value=1))
        birthday_day = draw(st.integers(min_value=1, max_value=31))
        birthday_month = draw(st.integers(min_value=1, max_value=12))
        birthday_year = draw(st.integers(min_value=datetime.date.today().year - 150,
                                         max_value=datetime.date.today().year + 1))

    class DataFactory(ModelFactory[Any]):
        __model__ = InputPackage
        data = Use(DatumFactory.batch, size=5)
        model = Use(InputModelFactory.build)

    request = DataFactory.build()
    return request.json()


def dummy_store(*args, **kwargs):
    return True


@patch.object(ModelMethod, 'store', dummy_store)
class TestModel(unittest.TestCase):
    """
    This is a test that checks whether the model can work its way from input package to desired output including
    image. Therefore, visualizer actually renders PNG data, so the deadline for a test is increased up to 1000 ms.
    JSON files are used both as an input and as an expected result
    """
    def setUp(self):
        self.model = Model()
        self.model.add_method('AMRDirect')

    def get_method_result(self, method, request):
        return json.loads(self.model.run_method(method, request))

    def test_get_description(self):
        description = self.model.get_description()
        self.assertEqual(description["type_id"], "models")
        self.assertNotEqual(description["container_id"], "")
        self.assertIsNotNone(description["container_id"])
        self.assertIn("AMRDirect", description)

    def test_run_method_end_to_end_correct(self):
        self.maxDiff = None
        with open('tests/amr_direct_risk_value/amr_test_correct.json') as f:
            amr_test_data = json.load(f)

        with open('tests/amr_direct_risk_value/amr_test_correct_result.json') as f:
            amr_test_result = json.load(f)

        self.assertEqual(
            self.get_method_result('AMRDirect', json.dumps(amr_test_data)),
            amr_test_result
        )

    def test_run_method_end_to_end_incorrect(self):
        self.maxDiff = None
        with open('tests/amr_direct_risk_value/amr_test_incorrect.json') as f:
            amr_test_data = json.load(f)

        with open('tests/amr_direct_risk_value/amr_test_incorrect_result.json') as f:
            amr_test_result = json.load(f)

        self.assertEqual(
            self.get_method_result('AMRDirect', json.dumps(amr_test_data)),
            amr_test_result
        )

    def test_add_method(self):
        pass  # TODO implements this

    @given(draw_data=build_correct_input_package())
    @settings(database=None, max_examples=1000)
    def test_run_method_extensive(self, draw_data):
        model_run_result = self.get_method_result('AMRDirect', draw_data)
        self.assertIsNotNone(model_run_result['model'])  # TODO refactor

    def test_martin_alekseevich(self):
        with open('tests/amr_direct_risk_value/martin_alekseevich.txt') as f:
            test_data = f.read()

        model_run_result = self.get_method_result('AMRDirect', test_data)
        self.assertIn('error', model_run_result)
        # model should return JSON-RPC Invalid request error, code -32600
        self.assertEqual(-32600, model_run_result['error']['code'])

    def test_nonexistent_method(self):
        model_run_result = self.get_method_result('NonExistentMethod', '{}')
        self.assertIn('error', model_run_result)
        # model should return JSON-RPC Method does not exist error, code -32601
        self.assertEqual(-32601, model_run_result['error']['code'])


if __name__ == "__main__":
    unittest.main()
