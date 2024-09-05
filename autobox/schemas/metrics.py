# from typing import Literal
# type: Literal["counter", "gauge", "histogram"]

from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    description: str
    type: str
    unit: str


class Metrics(BaseModel):
    metrics: list[Metric]
