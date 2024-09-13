from typing import Dict

from prometheus_client import Counter, Gauge, Histogram, Summary

from autobox.schemas.metrics import Metric

# Create metrics

# Counter metric (e.g., total clues discovered)
# clue_discovery_total = Counter(
#     "clue_discovery_total",
#     "Tracks the total number of clues discovered by Detective Graves during the investigation.",
# )

# # Gauge metric (e.g., suspect suspicion level)
# suspect_suspicion_level = Gauge(
#     "suspect_suspicion_level", "Gauges the level of suspicion for each suspect."
# )

# # Histogram metric (e.g., evidence analysis time in seconds)
# evidence_analysis_time = Histogram(
#     "evidence_analysis_time_seconds", "Time taken to analyze each piece of evidence."
# )

# # Summary metric (e.g., forensic analysis accuracy over time)
# forensic_analysis_accuracy = Summary(
#     "forensic_analysis_accuracy", "Assesses the accuracy of forensic analysis."
# )


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


# def run_simulation():
#     while True:
#         # Update metrics during simulation

#         # Increment the counter
#         clue_discovery_total.inc(random.randint(1, 5))

#         # Set gauge value
#         suspect_suspicion_level.set(random.uniform(0, 100))

#         # Record histogram value
#         evidence_analysis_time.observe(random.uniform(0.1, 3.0))

#         # Record summary value
#         forensic_analysis_accuracy.observe(random.uniform(80.0, 100.0))

#         # Sleep to simulate time between updates
#         time.sleep(5)


# if __name__ == "__main__":
#     # Start an HTTP server on port 8000 to expose the metrics
#     start_http_server(8000)
#     # Run the simulation
#     run_simulation()
