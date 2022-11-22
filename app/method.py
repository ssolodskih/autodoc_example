"""Class of the model method."""
from copy import deepcopy
from dataclasses import dataclass

from abstracts import ProtoMethod, IntermediateData
from data_definitions.internal_format import InternalFormat
from data_definitions.numedy import InputPackage, OutputPackage
from exceptions import ModelTypeCheckException, ModelValidationException, JSONRPCInternalError


@dataclass
class ModelMethod(ProtoMethod):
    def run(self, data: dict):
        self.result = IntermediateData()
        try:
            self.result.typechecker_result = self.typecheck(data)
            self.result.conversion_result = self.convert(self.result.typechecker_result)
            self.result.validation_result = self.validate(self.result.conversion_result)
            self.result.calculation_result = self.calculate(self.result.validation_result)
            self.result.visualizer_bytes = self.visualize(self.result.calculation_result)
        except (ModelValidationException, ModelTypeCheckException) as e:
            self.result.error = e.external_error
        except Exception as e:
            self.result.error = JSONRPCInternalError(data=str(e)).external_error

        self.store()

        reverse_conversion_result = self.restore(self.result)
        if hasattr(reverse_conversion_result, 'json'):
            method_run_result = reverse_conversion_result.json()
        else:
            method_run_result = str(reverse_conversion_result)

        return method_run_result

    def typecheck(self, data: dict = None) -> InputPackage:
        self.success = self.typechecker.check_types(data)
        return self.typechecker.result

    def convert(self, input_package: InputPackage) -> InternalFormat:
        self.converter.store(input_package)
        self.success = self.converter.convert()
        return self.converter.internal_data

    def validate(self, internal_data: InternalFormat) -> dict:
        validator = deepcopy(self.validator)
        self.success = validator.validate(internal_data.dict())
        return validator.document

    def calculate(self, calculation_source: dict) -> dict:
        self.success = self.calculator.calculate(calculation_source)
        return self.calculator.result

    def visualize(self, visualization_source: dict) -> bytes:
        self.visualizer.visualize(data=visualization_source)
        visualizer_bytes = self.visualizer.generate_base64()
        return visualizer_bytes

    def restore(self, method_result: IntermediateData) -> OutputPackage:
        if method_result.error is None:
            self.success = self.converter.restore_successful_run(method_result)
        else:
            self.success = self.converter.restore_erroneous_run(method_result.error)
        return self.converter.output_package

    def store(self) -> bool:
        self.storage_manager.store(self.result)
        #asyncio.run(self.storage_manager.store(self.result))
        return True
