from typing import List, Literal, Optional

from prometheus_client import CollectorRegistry
from pydantic import BaseModel, Field


class MetricDefinition(BaseModel):
    name: str
    description: str
    type: Literal["counter", "gauge", "histogram"]
    unit: str


class Metrics(BaseModel):
    metrics: list[MetricDefinition]


class MetricPanelOptions(BaseModel):
    displayLabels: List[str]


class MetricPanel(BaseModel):
    type: Literal[
        "graph",
        "stat",
        "gauge",
        "heatmap",
        "timeseries",
        "piechart",
        "barchart",
        "bargauge",
    ]
    expression: str
    legend_format: str
    options: Optional[MetricPanelOptions] = None


class Metric(BaseModel):
    name: str
    description: str
    prometheus_type: Literal["counter", "gauge", "histogram"]
    panels: List[MetricPanel]
    unit: str
    value: float = Field(default=0.0)
    collector_registry: CollectorRegistry = None

    class Config:
        arbitrary_types_allowed = True


class MetricCalculatorUpdate(BaseModel):
    metric_name: str
    value: float
    agent_name: str
    thinking_process: str


class MetricCalculator(BaseModel):
    update: list[MetricCalculatorUpdate]


class MetricResponse(BaseModel):
    name: str
    description: str
    type: Literal["counter", "gauge", "histogram"]
    unit: str
    value: float = Field(default=0.0)
