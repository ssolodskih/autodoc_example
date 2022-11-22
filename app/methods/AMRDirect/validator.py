from datetime import datetime
from enum import Enum, IntEnum
from itertools import groupby
from typing import List, Any

from pydantic import validator, ValidationError, conint

from abstracts import Validator
from data_definitions.errors import TimestampIncorrect, TimestampOutOfRangeError
from data_definitions.internal_format import InternalDatum, InternalFormat, InternalMetadata
from exceptions import ModelValidationException


class AMRChoices(IntEnum):
    positive = 2
    negative = 1
    unknown = 0


class AMRVariables(str, Enum):
    imp = 'imp'
    oxa_40_like = 'oxa_40_like'
    oxa_48_like = 'oxa_48_like'
    oxa_58_like = 'oxa_58_like'
    oxa_23_like = 'oxa_23_like'
    kpc = 'kpc'
    vim = 'vim'
    ndm = 'ndm'
    vana = 'vana'
    meca = 'meca'
    vanb = 'vanb'


class InternalDatumChecks(InternalDatum):
    variable: AMRVariables
    result: conint(strict=True, ge=0, le=2)  # AMRChoices
    measure_time: Any

    @validator('measure_time')
    def measure_time_incorrect(cls, measure_time):
        try:
            # parsed_measure_time = datetime.fromisoformat(measure_time)
            parsed_measure_time = datetime.strptime(str(measure_time), "%Y-%m-%d %H:%M:%S")
            return parsed_measure_time
        except Exception:
            raise TimestampIncorrect

    @validator('measure_time')
    def measure_time_in_the_future(cls, measure_time):
        if measure_time > datetime.now():
            raise TimestampOutOfRangeError
        return measure_time

    @validator('measure_time')
    def measure_time_expired(cls, start_date):
        max_months = 6
        end_date = datetime.today()
        num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if num_months > max_months:
            raise TimestampOutOfRangeError
        return start_date


class InternalDataChecks(InternalFormat):
    metadata: InternalMetadata
    data: List[InternalDatumChecks]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # the following code removes duplicate variable results so each variable
        # has only one result (the chronologically latest one)
        lst = sorted(self.data, key=lambda x: (x.variable, x.measure_time))
        for k, g in groupby(lst, key=lambda x: x.variable):
            group = list(g)

            if len(group) > 1:
                for idx in range(0, len(group)-1):
                    self.data.remove(group[idx])


class AMRDirectValidator(Validator):
    def validate(self, internal_data: dict) -> bool:
        """Specific data validation."""
        try:
            validated_data = InternalDataChecks(**internal_data)
            self.document = validated_data.dict()
            self.success = True
            return self.success
        except ValidationError as e:
            raise ModelValidationException(data=e.errors())
