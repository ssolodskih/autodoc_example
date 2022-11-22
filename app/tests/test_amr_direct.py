import datetime
import json
import unittest
from string import printable
from unittest.mock import patch

from hypothesis import given, settings, strategies as st

from method import ModelMethod
from model import Model

variable_correct_names = ['oxa_23_like', 'oxa_40_like', 'oxa_48_like', 'oxa_58_like', 'vana', 'vanb', 'imp',
                          'ndm', 'vim', 'kpc', 'meca']

future_datetimes = {
    'min': datetime.datetime.now() + datetime.timedelta(days=2),  # 2 days because of timezone-related delta
    'max': datetime.datetime.now() + datetime.timedelta(days=round(365.25 * 10))  # rounded 10 years in the future
}

datetimes_out_of_range = {
    'min': datetime.datetime.now() - datetime.timedelta(days=round(365.25 * 10)),  # rounded 10 years in the past
    'max': datetime.datetime.now() - datetime.timedelta(days=round(365.25 * 5))  # rounded 5 years in the past
}

correct_datetimes = {
    'min': datetime.datetime.now() - datetime.timedelta(days=round(30 * 6)),  # rounded 6 months in the past
    'max': datetime.datetime.now()
}


@st.composite
def build_correct_data(draw):
    birthday_day_min = 1
    birthday_day_max = 31
    birthday_month_min = 1
    birthday_month_max = 12
    birthday_year_min = datetime.datetime.now().year - 150  # we're not expecting to deal with mega-centenarians, right?
    birthday_year_max = datetime.datetime.now().year
    measurements = st.fixed_dictionaries({
        "id_": st.just('96c6117e-efe1-49a9-b341-adc564fba76d'),
        "variable": st.sampled_from(variable_correct_names),
        "result": st.sampled_from([0, 1, 2]),
        "measure_time": st.just(draw(st.datetimes(
            min_value=correct_datetimes['min'],
            max_value=correct_datetimes['max']
        )).strftime("%Y-%m-%d %H:%M:%S"))
    })

    return json.dumps({
        "metadata": {
            'birthday_day': draw(st.integers(min_value=birthday_day_min, max_value=birthday_day_max)),
            'birthday_month': draw(st.integers(min_value=birthday_month_min, max_value=birthday_month_max)),
            'birthday_year': draw(st.integers(min_value=birthday_year_min, max_value=birthday_year_max)),
            'gender_id': draw(st.integers(min_value=0, max_value=1)),
            'patient_id': draw(st.integers(min_value=1))
        },
        "data": [
            draw(measurements)
        ]
    })


def get_invalid_metadata(draw):
    birthday_day_min = 32
    birthday_day_max = 0
    birthday_month_min = 13
    birthday_month_max = 0
    birthday_year_min = datetime.datetime.now().year + 2
    birthday_year_max = datetime.datetime.now().year - 150
    return {
        "metadata": {
            'birthday_day': draw(st.one_of(
                st.integers(min_value=birthday_day_min),
                st.integers(max_value=birthday_day_max))
            ),
            'birthday_month': draw(st.one_of(
                st.integers(min_value=birthday_month_min),
                st.integers(max_value=birthday_month_max))
            ),
            'birthday_year': draw(st.one_of(
                st.integers(min_value=birthday_year_min),
                st.integers(max_value=birthday_year_max))
            ),
            'gender_id': draw(st.one_of(
                st.integers(min_value=2),
                st.integers(max_value=-1))),
            'patient_id': draw(st.integers(min_value=1))
        }
    }


def build_correct_datablock(draw):
    return {
        "data": [
            {
                "id_": draw(st.just('96c6117e-efe1-49a9-b341-adc564fba76d')),
                "variable": draw(st.sampled_from(variable_correct_names)),
                "result": draw(st.integers(min_value=0, max_value=1)),
                "measure_time": draw(st.datetimes(
                    min_value=correct_datetimes['min'],
                    max_value=correct_datetimes['max']
                )).strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }


def get_datablock_with_invalid_values(draw):
    res = build_correct_datablock(draw)
    res["data"][0]["result"] = draw(st.one_of(
        st.integers(min_value=3),
        st.integers(max_value=-1))
    )
    return res


def get_datablock_with_invalid_var_name(draw):
    res = build_correct_datablock(draw)
    res["data"][0]["measure_time"] = draw(st.text(max_size=100).filter(lambda x: x not in variable_correct_names))
    return res


def get_datablock_with_datetime_from_the_future(draw):
    res = build_correct_datablock(draw)
    res["data"][0]["variable"] = draw(st.datetimes(
        min_value=future_datetimes['min'],
        max_value=future_datetimes['max']
    )).strftime("%Y-%m-%d %H:%M:%S")
    return res


def get_datablock_with_timestamp_out_of_range(draw):
    res = build_correct_datablock(draw)
    res["data"][0]["measure_time"] = draw(st.datetimes(
        min_value=datetimes_out_of_range['min'],
        max_value=datetimes_out_of_range['max']
    )).strftime("%Y-%m-%d %H:%M:%S")
    return res


def get_datablock_with_absent_value(draw):
    res = build_correct_datablock(draw)
    res["data"][0]["result"] = None
    return res


def get_datablock_with_incorrect_datetime(draw):
    res = build_correct_datablock(draw)
    json = st.recursive(
        st.booleans() | st.floats() | st.text(printable),
        lambda children: st.lists(children) | st.dictionaries(st.text(printable), children),
    )
    res["data"][0]["measure_time"] = draw(json)
    return res


def get_datablock_with_value_incorrect(draw):
    res = build_correct_datablock(draw)
    json = st.recursive(
        st.text(printable),
        lambda children: st.lists(children) | st.dictionaries(st.text(printable), children),
    )
    res["data"][0]["result"] = draw(json)
    return res


@st.composite
def build_random_incorrect_data(draw):
    incorrect_part = draw(st.sampled_from(
        [
            get_invalid_metadata(draw),
            get_datablock_with_invalid_values(draw),
            get_datablock_with_invalid_var_name(draw),
            get_datablock_with_datetime_from_the_future(draw),
            get_datablock_with_absent_value(draw)
        ]
    ))
    correct_part = json.loads(draw(build_correct_data()))
    return json.dumps({**correct_part, **incorrect_part})


@st.composite
def build_data_value_out_of_range(draw):
    incorrect_part = draw(st.sampled_from(
        [
            get_datablock_with_invalid_values(draw)
        ]
    ))
    correct_part = json.loads(draw(build_correct_data()))
    return json.dumps({**correct_part, **incorrect_part})


@st.composite
def build_data_value_absent(draw):
    incorrect_part = draw(st.sampled_from(
        [
            get_datablock_with_absent_value(draw)
        ]
    ))
    correct_part = json.loads(draw(build_correct_data()))
    return json.dumps({**correct_part, **incorrect_part})


@st.composite
def build_data_timestamp_incorrect(draw):
    incorrect_part = draw(st.sampled_from(
        [
            get_datablock_with_incorrect_datetime(draw)
        ]
    ))
    correct_part = json.loads(draw(build_correct_data()))
    return json.dumps({**correct_part, **incorrect_part})


@st.composite
def build_data_timestamp_out_of_range(draw):
    incorrect_part = draw(st.sampled_from(
        [
            get_datablock_with_timestamp_out_of_range(draw)
        ]
    ))
    correct_part = json.loads(draw(build_correct_data()))
    return json.dumps({**correct_part, **incorrect_part})


@st.composite
def build_data_value_incorrect(draw):
    incorrect_part = draw(st.sampled_from(
        [
            get_datablock_with_value_incorrect(draw)
        ]
    ))
    correct_part = json.loads(draw(build_correct_data()))
    return json.dumps({**correct_part, **incorrect_part})


def dummy_store(*args, **kwargs):
    return True


@patch.object(ModelMethod, 'store', lambda x: True)
@patch('methods.AMRDirect.visualizer.AMRDirectVisualizer.format_selector', return_value='svg')
class TestAMRDirectMethod(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.model.add_method(
            "AMRDirect",
            typechecker=False,  # we supply data in internal format, so we don't need to check types and convert data
            converter=False
        )

    def get_method_result(self, method, request):
        return json.loads(self.model.run_method(method, request))

    @given(draw_data=build_correct_data())
    @settings(database=None, max_examples=200)
    def test_amr_direct_correct_random_data(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertIn("typechecker_result", model_method_result)
        self.assertIn("metadata", model_method_result["typechecker_result"])
        self.assertIn("data", model_method_result["typechecker_result"])
        self.assertIsNone(model_method_result["error"])

    @given(draw_data=build_random_incorrect_data())
    @settings(database=None, max_examples=200)
    def test_amr_direct_incorrect_random_data(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertNotIn("result", model_method_result)
        self.assertIn("error", model_method_result)

    @given(draw_data=build_data_timestamp_out_of_range())
    @settings(database=None, max_examples=200)
    def test_amr_direct_timestamp_out_of_range(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertIn("error", model_method_result)
        self.assertNotIn("result", model_method_result)
        self.assertEqual("timestamp_out_of_range", model_method_result['error']['data'][0]['internal_error_code'])

    @given(draw_data=build_data_timestamp_incorrect())
    @settings(database=None, max_examples=200)
    def test_amr_direct_timestamp_incorrect(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertIn("error", model_method_result)
        self.assertNotIn("result", model_method_result)
        self.assertEqual("timestamp_incorrect", model_method_result['error']['data'][0]['internal_error_code'])

    @given(draw_data=build_data_value_incorrect())
    @settings(database=None, max_examples=200)
    def test_amr_direct_value_incorrect(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertIn("error", model_method_result)
        self.assertNotIn("result", model_method_result)
        self.assertEqual("value_incorrect", model_method_result['error']['data'][0]['internal_error_code'])

    @given(draw_data=build_data_value_absent())
    @settings(database=None, max_examples=200)
    def test_amr_direct_value_absent(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertIn("error", model_method_result)
        self.assertNotIn("result", model_method_result)
        self.assertEqual("value_absent", model_method_result['error']['data'][0]['internal_error_code'])

    @given(draw_data=build_data_value_out_of_range())
    @settings(database=None, max_examples=200)
    def test_amr_direct_value_out_of_range(self, draw_data, mock):
        model_method_result = self.get_method_result("AMRDirect", draw_data)
        self.assertIn("error", model_method_result)
        self.assertNotIn("result", model_method_result)
        self.assertEqual("value_out_of_range", model_method_result['error']['data'][0]['internal_error_code'])


if __name__ == "__main__":
    unittest.main()
