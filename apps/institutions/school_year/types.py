from datetime import date
from typing import TypedDict


class CreateSchoolYearPayload(TypedDict, total=False):
    start_date: date
    end_date: date
