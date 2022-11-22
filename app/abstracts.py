"""Abstract classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pydantic import BaseModel
from typing import NamedTuple, Dict, Any
from datetime import datetime

from data_definitions.numedy import InputPackage, OutputPackage
from data_definitions.internal_format import InternalFormat
from exceptions import ExternalError


class IntermediateData(BaseModel):
    """
    Data class that stores input data from the client, all the intermediate outputs, output data
    and error message if any. Is used for communication of different parts of the method and for
    storing/logging data.
    """

    typechecker_result: InputPackage = None
    conversion_result: InternalFormat = None
    validation_result: Dict = None
    calculation_result: Dict = None
    visualizer_bytes: bytes = None
    error: ExternalError = None
    timestamp: datetime = None


@dataclass
class TypeChecker(ABC):
    """Checks types of input data."""

    result: InputPackage = None
    data_schema: dict = None
    errors: dict = field(default_factory=dict)

    @abstractmethod
    def check_types(self, input_data: dict) -> bool:
        """
        Checks field types in the incoming data against client-specific data schema.
        Data schemas are defined in data_definitions submodules.
        """


@dataclass
class Converter(ABC):
    """Converts data from various input formats to standard internal format."""

    internal_data: InternalFormat = None
    input_package: InputPackage = None
    output_package: OutputPackage = None

    @abstractmethod
    def store(self, input_package: InputPackage) -> bool:
        """Stores full incoming data package for further use."""

    @abstractmethod
    def convert(self) -> bool:
        """Performs actual conversion from external to internal format."""

    @abstractmethod
    def restore_successful_run(self, method_result: IntermediateData) -> bool:
        """
        Restores data from internal format to output client-specific format in case of successful
        calculation.
        """

    @abstractmethod
    def restore_erroneous_run(self, error: ExternalError) -> bool:
        """Restores data from internal format to output client-specific format in case of an error."""


@dataclass
class Validator(ABC):
    """Validates data in standard internal format."""

    document: dict = field(default_factory=dict)
    success: bool = False

    @abstractmethod
    def validate(self, internal_data: dict) -> bool:
        """Performs data validation. All logic not defined in Pydantic validator is implemented here."""


@dataclass
class Calculator(ABC):
    """Performs calculations necessary for further steps."""

    result: dict = None

    @abstractmethod
    def calculate(self, data: dict) -> bool:
        """Performs actual calculations."""


@dataclass
class Visualizer(ABC):
    """Performs visualization that are necessary for this method based on calculation results and metadata."""
    data: dict = None

    @abstractmethod
    def visualize(self, data: dict) -> bool:
        """Extracts data from calculation results and prepares sources needed for rendering image(s)."""
        pass

    @abstractmethod
    def render_png(self) -> bytes:
        """Renders visualization results to PNG format."""
        pass

    @abstractmethod
    def save_png(self, filename: str) -> bool:
        """Saves rendered PNG to the file system."""
        pass

    @abstractmethod
    def generate_base64(self) -> bytes:
        """Converts supplied visualization result to Base64-encoded string"""
        pass


@dataclass
class StorageManager(ABC):
    """Stores result of model work in a database or filesystem."""

    conn_config: dict = None

    @abstractmethod
    def store(self, data_to_store: IntermediateData) -> bool:
        """Stores data. The storage format and engine are defined in the implementation."""
        pass


class FactoryRunResult(NamedTuple):
    """Helper class for method factory's output."""

    visualizer: Visualizer
    calculator: Calculator
    validator: Validator
    type_checker: TypeChecker
    storage_manager: StorageManager
    converter: Converter


class MethodFactory(ABC):
    """Creates method for the model."""

    @abstractmethod
    def get_type_checker(self) -> TypeChecker:
        """Returns type checker."""

    @abstractmethod
    def get_converter(self) -> Converter:
        """Returns converter."""

    @abstractmethod
    def get_validator(self) -> Validator:
        """Returns validator."""

    @abstractmethod
    def get_calculator(self) -> Calculator:
        """Returns calculator."""

    @abstractmethod
    def get_visualizer(self) -> Visualizer:
        """Returns visualizer."""

    @abstractmethod
    def get_storage_manager(self) -> StorageManager:
        """Returns storage manager."""

    @abstractmethod
    def run_factory(self) -> FactoryRunResult:
        """Returns all objects produced by a factory embedded in FactoryRunResult structure."""


@dataclass
class ProtoMethod(ABC):
    """
    Class for the method of the model.

    :param typechecker: type checker object
    :param converter: converter object
    :param validator: validator object
    :param calculator: calculator object
    :param visualizer: visualizer object
    :param storage_manager: storage manager object
    :param params: method parameters
    """

    name: str
    typechecker: TypeChecker
    converter: Converter
    validator: Validator
    calculator: Calculator
    visualizer: Visualizer = None
    storage_manager: StorageManager = None
    success: bool = True
    params: dict = None
    result: IntermediateData = None

    @abstractmethod
    def run(self, data: dict):
        """Executes the method."""

    @abstractmethod
    def typecheck(self, data: dict = None) -> InputPackage:
        """Uses Typechecker to parse input data and check it for type errors."""

    @abstractmethod
    def convert(self, input_package: InputPackage) -> InternalFormat:
        """Uses Converter to convert data from input format to internal format."""

    @abstractmethod
    def validate(self, internal_data: InternalFormat) -> dict:
        """Uses Validator to validate the data."""

    @abstractmethod
    def calculate(self, calculation_source: dict) -> dict:
        """Uses Calculator to process the data."""

    @abstractmethod
    def visualize(self, visualization_source: dict) -> bytes:
        """Uses Visualizer to generate image[s]."""

    @abstractmethod
    def store(self) -> bool:
        """Uses StorageManager to store the data in a long-term storage."""

    @abstractmethod
    def restore(self, method_result: IntermediateData) -> OutputPackage:
        """Uses Converter to convert data back from internal state back to the format of a client."""


@dataclass
class ProtoModel(ABC):
    """
    Model class. Performs all the actions necessary to convert input data to desired result.
    These include:
    - data type checks according to the client-specific data format,
    - conversion to model internal format,
    - calculations based upon these data,
    - data visualization (optional),
    - storage of iinput, intermediate, and output data as well as error information (optional)
    """
    description: dict = field(default_factory=dict)
    methods: Dict[str, ProtoMethod] = field(default_factory=dict)
    type_id: str = "models"

    @abstractmethod
    def get_description(self) -> dict:
        """
        Returns model description

        :return: description of the model and its methods
        """

    @abstractmethod
    def add_method(self, name: str, params: list = None) -> bool:
        """
        Adds particular method to the model's list of methods via composition

        :param name: method name
        :param params: method parameters
        :return: method addition status
        """

    @abstractmethod
    def run_method(self, name: str, data: str) -> str:
        """
        Executes method for the given set of data

        :param name: method name
        :param data: data in client-specific format
        :return: method run result
        """
