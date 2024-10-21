from typing import Dict

from autobox.schemas.metrics import Metric, MetricResponse
from autobox.transformations.metric_to_response import (
    transform as transform_single_metric,
)


def transform(metrics: Dict[str, Metric]) -> MetricResponse:
    return [transform_single_metric(metric) for metric in metrics.values()]
