from typing import Dict

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, Summary

from autobox.schemas.metrics import Metric


def metric_exists(metric_name):
    for collector in REGISTRY._collector_to_names.items():
        if metric_name in collector[1]:
            return True
    return False


def create_prometheus_metrics(metrics: Dict[str, Metric]):
    labels = ["simulation_id", "simulation_name"]
    for name, metric in metrics.items():
        if not metric_exists(name):
            if metric.type == "counter":
                metric.collector_registry = Counter(name, metric.description, labels)
            elif metric.type == "gauge":
                metric.collector_registry = Gauge(name, metric.description, labels)
            elif metric.type == "histogram":
                metric.collector_registry = Histogram(name, metric.description, labels)
            elif metric.type == "summary":
                metric.collector_registry = Summary(name, metric.description, labels)
