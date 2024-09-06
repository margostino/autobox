from typing import Dict

from pydantic import BaseModel

from autobox.schemas.metrics import Metric


class MetricsCache(BaseModel):
    metrics: Dict[str, Metric]

    def update(self, metric_name: str, value: float):
        metric = self.metrics.get(metric_name)
        if metric is not None:
            metric.value = value
        # else:
        # TODO
