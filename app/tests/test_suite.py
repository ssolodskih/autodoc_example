import unittest
from tests.test_amr_direct import TestAMRDirectMethod
from tests.test_calculator import TestCalculator
from tests.test_error_handling import TestErrorHandling
from tests.test_model import TestModel
from tests.test_visualizer import TestVisualizer


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestAMRDirectMethod))
    test_suite.addTest(unittest.makeSuite(TestCalculator))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    test_suite.addTest(unittest.makeSuite(TestModel))
    test_suite.addTest(unittest.makeSuite(TestVisualizer))
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
