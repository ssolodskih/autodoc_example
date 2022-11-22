import json
import unittest

from methods.AMRDirect.calculator import AMRDirectCalculator


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = AMRDirectCalculator()

    def test_calculate(self):
        with open('tests/amr_direct_risk_value/amr_calc_examples.json') as json_file:
            examples = json.load(json_file)
            for example in examples:
                if 'request' in example and example['request'] is not None:
                    self.calculator.calculate(data=example['request'])
                    self.assertEqual(example['response'], self.calculator.result)


if __name__ == "__main__":
    unittest.main()
