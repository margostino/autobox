from typing import Dict

from grafana_client import AsyncGrafanaApi

from autobox.schemas.metrics import Metric

# TODO: while in local, then pass this as config
grafana = AsyncGrafanaApi.from_url("http://admin:admin@localhost:3000")


def create_panel(metric: Metric, panel_id: int, x: int, y: int):
    panel = {
        "id": panel_id,
        "title": metric.name,
        "type": "graph",  # This can be changed dynamically for different visualizations
        "datasource": "Prometheus",
        "gridPos": {"h": 9, "w": 12, "x": x, "y": y},
        "targets": [
            {"expr": f"{metric.name}", "legendFormat": metric.name, "refId": "A"}
        ],
        "fieldConfig": {
            "defaults": {"unit": metric.unit, "description": metric.description}
        },
    }

    if metric.type == "counter":
        panel["type"] = "stat"
    elif metric.type == "gauge":
        panel["type"] = "gauge"
    elif metric.type == "histogram":
        panel["type"] = "heatmap"  # A heatmap might be more suitable for histogram

    return panel


async def create_grafana_dashboard(simulation_name_id: str, metrics: Dict[str, Metric]):
    panels = []
    panel_id = 1
    x, y = 0, 0

    for _, metric in metrics.items():
        panel = create_panel(metric, panel_id, x, y)
        panels.append(panel)

        x += 12
        if x >= 24:
            x = 0
            y += 9
        panel_id += 1

    new_dashboard = {
        "dashboard": {
            "id": None,
            "title": f"{simulation_name_id} Metrics",
            "panels": panels,
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "5s",
        },
        "folderId": 0,
        "overwrite": False,
    }

    return await grafana.dashboard.update_dashboard(new_dashboard)
