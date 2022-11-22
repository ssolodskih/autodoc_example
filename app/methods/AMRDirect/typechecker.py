from pydantic import ValidationError

from abstracts import TypeChecker
from exceptions import ModelTypeCheckException
from data_definitions.numedy import InputPackage


class AMRDirectTypeChecker(TypeChecker):
    def check_types(self, input_data: dict) -> bool:
        try:
            input_package = InputPackage(**input_data)
            self.result = input_package
            return True
        except ValidationError as e:
            raise ModelTypeCheckException(data=e.errors())
