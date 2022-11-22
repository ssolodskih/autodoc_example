"""Factory class for AMR Direct method."""
from abstracts import MethodFactory, TypeChecker, Converter, Validator, Calculator, Visualizer, StorageManager, FactoryRunResult
from dummies import DummyConverter, DummyValidator, DummyTypeChecker
from methods.AMRDirect.calculator import AMRDirectCalculator
from methods.AMRDirect.converter import AMRDirectConverter
from methods.AMRDirect.typechecker import AMRDirectTypeChecker
from methods.AMRDirect.validator import AMRDirectValidator
from methods.AMRDirect.visualizer import AMRDirectVisualizer
from methods.AMRDirect.storagemanager import AsyncMongoStorageManager, LoggingStorageManager, SyncMongoStorageManager
from config import settings


class AMRDirectStorageManager(StorageManager):
    def store(self):
        return True


class AMRDirectMethodFactory(MethodFactory):
    def __init__(self, typechecker: bool = True, converter: bool = True, validator: bool = True):
        self.typechecker = typechecker
        self.converter = converter
        self.validator = validator

    def get_type_checker(self) -> TypeChecker:
        if self.typechecker:
            return AMRDirectTypeChecker()
        else:
            return DummyTypeChecker()

    def get_converter(self) -> Converter:
        if self.converter:
            return AMRDirectConverter()
        else:
            return DummyConverter()

    def get_validator(self) -> Validator:
        if self.validator:
            return AMRDirectValidator()
        else:
            return DummyValidator()

    def get_calculator(self) -> Calculator:
        return AMRDirectCalculator()

    def get_visualizer(self) -> Visualizer:
        return AMRDirectVisualizer(height=settings.get('AMR_RENDER_HEIGHT'), width=settings.get('AMR_RENDER_WIDTH'))

    def get_storage_manager(self) -> StorageManager:
        return SyncMongoStorageManager({'filename': ''})

    def run_factory(self) -> FactoryRunResult:
        return FactoryRunResult(
            visualizer=self.get_visualizer(),
            type_checker=self.get_type_checker(),
            calculator=self.get_calculator(),
            validator=self.get_validator(),
            converter=self.get_converter(),
            storage_manager=self.get_storage_manager()
        )
