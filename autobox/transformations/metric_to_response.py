from autobox.schemas.metrics import Metric, MetricResponse


def transform(metric: Metric) -> MetricResponse:
    return MetricResponse(
        name=metric.name,
        description=metric.description,
        type=metric.type,
        unit=metric.unit,
        value=metric.value,
    )
