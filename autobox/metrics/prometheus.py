from typing import Dict

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, Summary

from autobox.schemas.metrics import Metric


def metric_exists(metric_name):
    for collector in REGISTRY._collector_to_names.items():
        if metric_name in collector[1]:
            return True
    return False


def get_existing_metric(metric_name):
    if metric_name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[metric_name]
    return None


def create_prometheus_metrics(metrics: Dict[str, Metric]):
    labels = ["simulation_id", "simulation_name", "agent_name"]
    for name, metric in metrics.items():
        existing_metric = get_existing_metric(name)
        if existing_metric:
            metric.collector_registry = existing_metric
        else:
            if metric.prometheus_type == "counter":
                metric.collector_registry = Counter(name, metric.description, labels)
            elif metric.prometheus_type == "gauge":
                metric.collector_registry = Gauge(name, metric.description, labels)
            elif metric.prometheus_type == "histogram":
                metric.collector_registry = Histogram(name, metric.description, labels)
            elif metric.prometheus_type == "summary":
                metric.collector_registry = Summary(name, metric.description, labels)
