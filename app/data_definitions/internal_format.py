"""Definitions of internal data model."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, UUID4, PositiveInt, conint


class InternalDatum(BaseModel):
    id_: UUID4
    variable: str
    result: int
    measure_time: datetime

    @property
    def expired(self) -> bool:
        end_date = datetime.today()
        start_date = self.measure_time
        num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        return num_months > 6


class InternalMetadata(BaseModel):
    birthday_day: PositiveInt
    birthday_month: PositiveInt
    birthday_year: PositiveInt
    gender_id: conint(strict=True, ge=0, le=1)
    patient_id: PositiveInt


class InternalFormat(BaseModel):
    metadata: InternalMetadata
    data: List[InternalDatum]

    def remove_expired(self):
        for datum in self.data:
            if datum.expired:
                self.data.remove(datum)
