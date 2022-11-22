"""Dummy classes for unit-tests."""

from abstracts import Validator, Converter, TypeChecker, IntermediateData
from data_definitions.errors import ExternalError
from data_definitions.internal_format import InternalFormat
from data_definitions.numedy import InputPackage, OutputPackage


class DummyTypeChecker(TypeChecker):
    """Dummy type checker. Simply copies data from input to result without any changes."""

    def check_types(self, input_data: dict) -> bool:
        self.result = input_data
        return True


class DummyConverter(Converter):
    """Dummy converter. Copies data from input to result without any changes. Performa reverse operation likewise."""

    def store(self, input_package: InputPackage) -> bool:
        self.input_package = input_package
        return True

    def convert(self) -> bool:
        self.internal_data = InternalFormat.construct(**self.input_package)
        return True

    def restore_successful_run(self, method_result: IntermediateData) -> bool:
        self.output_package = method_result
        return True

    def restore_erroneous_run(self, error: ExternalError) -> bool:
        self.output_package = error
        return True


class DummyValidator(Validator):
    """Dummy validator. Simply copies data from input to document without any changes."""

    def validate(self, internal_data: dict) -> bool:
        self.document = internal_data
        return self.success
