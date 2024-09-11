from typing import Dict, Literal

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


class MetricCalculatorUpdate(BaseModel):
    metric_name: str
    value: float
    thinking_process: str


class MetricCalculator(BaseModel):
    update: list[MetricCalculatorUpdate]


class MetricsResponse(BaseModel):
    metrics: Dict[str, Metric] = Field(default_factory=dict)
