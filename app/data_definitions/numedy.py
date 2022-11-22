"""Definitions of data models (input data, output data)."""

from datetime import datetime
from typing import List, Optional, Literal
from uuid import uuid4

from pydantic import BaseModel, PositiveInt, Field, UUID4, conint

from data_definitions.errors import ErrorResponse


class InputModel(BaseModel):
    service_name: Literal['bioviewer']
    create_time: datetime
    arguments_connection_item_id: int
    arguments_connection_result_id: int
    arguments_group_id: int
    group_technical_name: Optional[str] = None
    arguments_group_result_id: int
    service_item_id: int
    service_result_id: int
    model_item_id: int
    technical_model_name: Optional[str]
    bioviewer_model_item_id: int
    bioviewer_model_result_id: Optional[int]
    bioviewer_run_item_id: int
    bioviewer_run_result_id: Optional[int]
    birthday_day: PositiveInt
    birthday_month: PositiveInt
    birthday_year: PositiveInt
    gender_id: conint(ge=0, le=1)
    patient_id: PositiveInt


class ProtoDatum(BaseModel):
    id_: UUID4 = Field(default_factory=uuid4)
    arguments_type: str
    id_block_argument: Optional[str] = None
    id_result_argument: int
    id_result: int
    id_anatomy_addon: Optional[int] = None
    name_anatomy_addon: Optional[str] = None
    id_anatomy_localization: Optional[int] = None
    name_anatomy_localization: Optional[int] = None
    result: int
    reference_interval_min: Optional[int]
    reference_interval_max: Optional[int]
    measure_time: datetime


class InputPackage(BaseModel):
    model: InputModel
    data: List[ProtoDatum]


class OutputModelImage(BaseModel):
    antibiotic_resist: bytes = ''.encode()


class OutputDatumImage(BaseModel):
    reference_interval_type_3: bytes = Field(''.encode(), alias='img')


class OutputModel(BaseModel):
    service_name: Literal['bioviewer']
    run_id: Optional[int]
    create_time: datetime
    bioviewer_model_item_id: int
    bioviewer_model_result_id: Optional[int]
    bioviewer_run_item_id: int
    bioviewer_run_result_id: Optional[int]
    model_item_id: int
    model_result_id: Optional[int]
    technical_model_name: Optional[str]
    patient_id: PositiveInt
    image: Optional[List[OutputModelImage]]
    error: Optional[ErrorResponse]


class OutputDatum(BaseModel):
    arguments_type: str
    id_result: int
    id_anatomy_addon: Optional[int] = None
    name_anatomy_addon: Optional[str] = None
    id_anatomy_localization: Optional[int] = None
    name_anatomy_localization: Optional[int] = None
    result: Optional[float] = None
    image: Optional[List[OutputDatumImage]]
    measure_time: datetime


class OutputPackage(BaseModel):
    model: OutputModel
    data: Optional[List[OutputDatum]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
