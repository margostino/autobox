import json
import os
from typing import Dict, List

from openai import OpenAI

from autobox.core.agents.worker import Worker
from autobox.core.prompts.metrics_definition import prompt
from autobox.schemas.metrics import Metric, Metrics

# from autobox.server import logger


def define_metrics(
    name: str,
    path: str,
    workers: List[Worker],
    task: str,
    orchestrator_name: str,
    orchestrator_instruction: str,
    openai: OpenAI,
) -> Dict[str, Metric]:

    full_path = os.path.join(path, f"{name}.json")

    agent_content = json.dumps(
        [{"name": worker.name, "backstory": worker.backstory} for worker in workers]
    )
    completion_messages = [
        {"role": "system", "content": prompt()},
        {
            "role": "user",
            "content": f"Simulation TASK: {task}",
        },
        {
            "role": "user",
            "content": f"Simulation ORCHESTRATOR: name> {orchestrator_name}, instructions> {orchestrator_instruction}",
        },
        {"role": "user", "content": f"Simulation AGENTS: {agent_content}"},
    ]
    completion = openai.beta.chat.completions.parse(
        messages=completion_messages,
        model="gpt-4o-2024-08-06",
        temperature=0,
        response_format=Metrics,
    )
    metric_definitions = completion.choices[0].message.parsed

    metrics = {
        metric.name: Metric(
            name=metric.name,
            description=metric.description,
            type=metric.type,
            unit=metric.unit,
        ).model_dump()
        for metric in metric_definitions.metrics
    }

    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)
    except IOError as e:
        # logger.error(f"Error saving metrics to file: {e}")
        print(f"Error saving metrics to file: {e}")

    return metrics
