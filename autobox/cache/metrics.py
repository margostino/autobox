from typing import Dict

from pydantic import BaseModel, Field

from autobox.schemas.metrics import Metric


class MetricsCache(BaseModel):
    metrics: Dict[str, Metric] = Field(default_factory=dict)

    def update(self, metric_name: str, value: float):
        metric = self.metrics.get(metric_name, None)
        if metric is not None:
            metric.value = value
        # else:
        # TODO

    def init_metrics(self, metrics: Dict[str, Metric]):
        self.metrics = metrics

    async def get_all(self):
        return self.metrics
