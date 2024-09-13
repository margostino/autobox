from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from starlette.responses import Response


def handle_prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
