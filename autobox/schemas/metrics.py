from typing import Literal

from pydantic import BaseModel, Field


class MetricDefinition(BaseModel):
    name: str
    description: str
    type: Literal["counter", "gauge", "histogram"]
    unit: str


class Metrics(BaseModel):
    metrics: list[MetricDefinition]


class Metric(BaseModel):
    name: str
    description: str
    type: Literal["counter", "gauge", "histogram"]
    unit: str
    value: float = Field(default=0.0)
