import json
import os
from typing import Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from autobox.common.logger import Logger
from autobox.core.agents.worker import Worker
from autobox.core.prompts.metrics_definition import prompt
from autobox.schemas.metrics import Metric, Metrics

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=4)


class MetricCollector(BaseModel):
    logger: Logger

    def load_metrics_for_simulation(
        self,
        name: str,
        path: str,
        workers: List[Worker],
        task: str,
        orchestrator_name: str,
        orchestrator_instruction: str,
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
        else:
            metric_definitions = self.define_metrics(
                workers, task, orchestrator_name, orchestrator_instruction
            )
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
                self.logger.error(f"Error saving metrics to file: {e}")

            return metrics

    def define_metrics(
        self,
        workers: List[Worker],
        task: str,
        orchestrator_name: str,
        orchestrator_instruction: str,
    ) -> Dict[str, Metric]:
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
        return completion.choices[0].message.parsed
