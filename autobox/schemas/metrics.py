from typing import Literal

from prometheus_client import CollectorRegistry
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
    collector_registry: CollectorRegistry = None

    class Config:
        arbitrary_types_allowed = True


class MetricCalculatorUpdate(BaseModel):
    metric_name: str
    value: float
    thinking_process: str


class MetricCalculator(BaseModel):
    update: list[MetricCalculatorUpdate]


class MetricResponse(BaseModel):
    name: str
    description: str
    type: Literal["counter", "gauge", "histogram"]
    unit: str
    value: float = Field(default=0.0)
