import json
import os
from typing import Dict, Optional

from pydantic import ValidationError

from autobox.schemas.metrics import Metric


def load_metrics(
    name: str,
    path: str,
) -> Optional[Dict[str, Metric]]:
    full_path = os.path.join(path, f"{name}.json")

    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                metrics: Dict[str, Metric] = {
                    key: Metric(**value) for key, value in data.items()
                }
                return metrics
        except (FileNotFoundError, json.JSONDecodeError, ValidationError, IOError):
            return None
    return None
