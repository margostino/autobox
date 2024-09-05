from typing import Literal

from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    description: str
    type: Literal["counter", "gauge", "histogram"]
    unit: str


class Metrics(BaseModel):
    metrics: list[Metric]
