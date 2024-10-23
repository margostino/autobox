from typing import Dict

import requests
from grafana_client import AsyncGrafanaApi

from autobox.schemas.metrics import Metric

# TODO: while in local, then pass this as config
grafana = AsyncGrafanaApi.from_url("http://admin:admin@localhost:3000")


def create_panel_by_type(
    metric: Metric, panel_id: int, x: int, y: int, simulation_id: str
):
    expr = f'avg by(agent_name) (max({metric.name}{{simulation_id="{simulation_id}"}}))'
    panel = {
        "id": panel_id,
        "title": metric.name,
        "type": "graph",  # This can be changed dynamically for different visualizations
        "datasource": "Prometheus",
        "gridPos": {"h": 9, "w": 12, "x": x, "y": y},
        "targets": [{"expr": expr, "legendFormat": "total", "refId": "A"}],
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


def create_timeseries_panel(
    metric: Metric, panel_id: int, x: int, y: int, simulation_id: str
):
    expr = f'avg by(agent_name) (rate({metric.name}{{simulation_id="{simulation_id}"}}[$__rate_interval]))'
    panel = {
        "id": panel_id,
        "title": f"{metric.name} ({metric.unit})",
        "description": metric.description,
        "type": "timeseries",
        "datasource": "Prometheus",
        "gridPos": {"h": 9, "w": 12, "x": x, "y": y},
        "targets": [{"expr": expr, "legendFormat": "{{agent_name}}", "refId": "A"}],
        "fieldConfig": {
            # "defaults": {"unit": metric.unit, "description": metric.description}
            "defaults": {"description": metric.description}
        },
    }
    return panel


# TODO: parse and use the panels configuration from the metric directly
def create_panels(metric: Metric, simulation_id: str):
    panels = []
    panel_id = 1
    x, y = 0, 0

    for metric_panel in metric.panels:
        expr = metric_panel.expression.replace("{simulation_id}", simulation_id)
        panel = {
            "id": panel_id,
            "title": f"{metric.name} ({metric.unit})",
            "description": metric.description,
            "type": metric_panel.type,
            "datasource": "Prometheus",
            "gridPos": {"h": 9, "w": 12, "x": x, "y": y},
            "targets": [
                {
                    "expr": expr,
                    "legendFormat": metric_panel.legend_format,
                    "refId": "A",
                }
            ],
            "fieldConfig": {
                # "defaults": {"unit": metric.unit, "description": metric.description}
                "defaults": {"description": metric.description}
            },
        }
        if metric_panel.options:
            panel["options"] = {"displayLabels": metric_panel.options.displayLabels}

        panels.append(panel)
        x += 12
        if x >= 24:
            x = 0
            y += 9
        panel_id += 1

    return panels


def create_public_dashboard(uid, slug):
    snapshot_url = f"http://localhost:3000/api/dashboards/uid/{uid}/public-dashboards"

    request = {
        "uid": slug,
        "timeSelectionEnabled": False,
        "isEnabled": True,
        "annotationsEnabled": False,
        "share": "public",
    }

    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer glsa_Mlukvnji8eE0P2TIQ9x28wUNwuEZNwdK_2152b4e2",
    }
    response = requests.post(snapshot_url, json=request, headers=headers, timeout=10)

    if response.status_code == 200:
        data = response.json()
        access_token = data["accessToken"]
        public_url = (
            f"http://localhost:3000/public-dashboards/{access_token}?orgId=1&refresh=5s"
        )
        return public_url
    else:
        print(f"Error creating snapshot: {response.content}")
        return None


async def create_grafana_dashboard(
    simulation_name_id: str,
    simulation_id: str,
    metrics: Dict[str, Metric],
):
    panels = []

    for _, metric in metrics.items():
        metric_panels = create_panels(metric, simulation_id)
        panels += metric_panels

    new_dashboard = {
        "dashboard": {
            "id": None,
            "title": f"{simulation_name_id} ({simulation_id})",
            "panels": panels,
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "5s",
            "time": {"from": "now-10m", "to": "now"},
        },
        "folderId": 0,
        "overwrite": True,
    }

    internal_dashboard_response = await grafana.dashboard.update_dashboard(
        new_dashboard
    )
    public_dashboard_url = create_public_dashboard(
        internal_dashboard_response["uid"], internal_dashboard_response["slug"]
    )

    # TODO: do it properly and support remote servers
    internal_dashboard_url = (
        f"http://localhost:3000{internal_dashboard_response['url']}?orgId=1&refresh=5s"
    )

    return (
        internal_dashboard_url,
        public_dashboard_url,
    )
