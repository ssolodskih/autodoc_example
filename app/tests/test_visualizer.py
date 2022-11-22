import json
import unittest
from pathlib import Path

from methods.AMRDirect.visualizer import AMRDirectVisualizer


class TestVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = AMRDirectVisualizer()

    def test_visualize(self):
        print(Path.cwd())
        with open('tests/amr_direct_risk_value/amr_vis_examples.json') as json_file:
            examples = json.load(json_file)
            for example in examples:
                if 'request' in example and example['request'] is not None:
                    self.visualizer.visualize(data=example['request'])
                    visualizer_bytes = self.visualizer.generate_base64()
                    self.assertEqual(example['response'], visualizer_bytes)


if __name__ == "__main__":
    unittest.main()
