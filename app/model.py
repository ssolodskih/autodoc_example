"""Model class."""
import json
import socket
from json import JSONDecodeError

from abstracts import ProtoModel
from exceptions import JSONRPCMethodNotFound, JSONRPCInvalidRequest
from method import ModelMethod
from methods.AMRDirect.factory import AMRDirectMethodFactory


class AMRIndirectMethodFactory:  # stub for another AMR method
    pass


class Model(ProtoModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = {
            "type_id": self.type_id,
            "container_id": socket.gethostname()
        }

    def get_description(self) -> dict:
        description = self.description
        for method in self.methods:
            description[method] = self.methods[method].params  # TODO implement this
        return description

    def add_method(self, name: str, params: dict = None, **kwargs) -> bool:
        """
        It takes a method name, and a dictionary of parameters, and adds a method to the model

        :param name: The name of the method
        :type name: str
        :param params: dict = None,
        :type params: dict
        :return: A boolean value.
        """
        method_factories = {
            "AMRIndirect": AMRIndirectMethodFactory(),
            'AMRDirect': AMRDirectMethodFactory(**kwargs)
        }

        if name in method_factories:
            method_factory = method_factories[name]
            factory_result = method_factory.run_factory()
            method = ModelMethod(name=name,
                                 typechecker=factory_result.type_checker,
                                 converter=factory_result.converter,
                                 validator=factory_result.validator,
                                 calculator=factory_result.calculator,
                                 visualizer=factory_result.visualizer,
                                 storage_manager=factory_result.storage_manager)

            self.methods[name] = method
            self.methods[name].params = params
            return True
        else:
            return False

    def run_method(self, name: str, data: str) -> str:
        try:
            data = json.loads(data)
            result = self.methods[name].run(data)
        except KeyError:
            result = JSONRPCMethodNotFound().external_error.json()
        except JSONDecodeError as e:
            result = JSONRPCInvalidRequest(internal_error_code='value_incorrect',
                                           param_name='input_package',
                                           message=str(e)).external_error.json()

        return result
