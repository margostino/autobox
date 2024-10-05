from typing import Dict

from prometheus_client import Counter, Gauge, Histogram, Summary

from autobox.schemas.metrics import Metric


def create_prometheus_metrics(metrics: Dict[str, Metric]):
    for name, metric in metrics.items():
        if metric.type == "counter":
            metric.collector_registry = Counter(name, metric.description)
        elif metric.type == "gauge":
            metric.collector_registry = Gauge(name, metric.description)
        elif metric.type == "histogram":
            metric.collector_registry = Histogram(name, metric.description)
        elif metric.type == "summary":
            metric.collector_registry = Summary(name, metric.description)
