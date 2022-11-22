"""Definitions of error message model."""

from typing import List, Optional
from pydantic import BaseModel, PydanticValueError


class TimestampOutOfRangeError(PydanticValueError):
    code = 'timestamp_out_of_range'
    msg_template = 'Timestamp out of range'


class GenderOutOfRangeError(PydanticValueError):
    code = 'gender_out_of_range'
    msg_template = 'Gender value out of range, must be 0 or 1'


class TimestampIncorrect(PydanticValueError):
    code = 'timestamp_incorrect'
    msg_template = 'Timestamp incorrect, must be an ISO standard string'


class ExternalErrorDatum(BaseModel):
    param_name: str
    internal_error_code: str
    message: str


class ExternalError(BaseModel):
    code: int
    message: str
    data: Optional[List[ExternalErrorDatum | str]]


class ErrorResponse(BaseModel):
    id: int
    error: ExternalError
