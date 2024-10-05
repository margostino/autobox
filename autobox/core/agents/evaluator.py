import json

from autobox.core.agents.base import BaseAgent
from autobox.core.prompts.metrics_calculator import METRICS_CALCULATOR_PROMPT
from autobox.core.prompts.summary import SUMMARY_PROMPT
from autobox.schemas.message import Message
from autobox.schemas.metrics import MetricCalculator
from autobox.utils.console import spin


class Evaluator(BaseAgent):
    simulation_id: str = None
    simulation_name: str = None

    async def handle_message(self, message: Message):
        from autobox.cache.cache import Cache

        cache = await Cache.simulation().get_simulation_status(self.simulation_id)
        json_message_value = json.loads(message.value)

        metrics = {
            name: metric.model_dump_json(exclude="collector_registry")
            for name, metric in cache.metrics.items()
        }

        if "is_end" in json_message_value and json_message_value["is_end"]:
            final_completion = json_message_value["final_completion"]
            memory = json_message_value["memory"]
            chat_completion_messages = [
                {
                    "role": "user",
                    "content": f"FINAL RESULT: {final_completion}",
                },
                {
                    "role": "user",
                    "content": f"METRICS: {json.dumps(metrics)}",
                },
                {
                    "role": "user",
                    "content": f"MEMORY: {memory}",
                },
            ]
            completion = (
                spin(
                    f"🧠 Evaluator {self.name} ({self.id}) is thinking...",
                    lambda: self.llm.think(
                        thinker=self.name,
                        messages=chat_completion_messages,
                        prompt_name=SUMMARY_PROMPT,
                    ),
                )
                if self.is_local_mode
                else self.llm.think(
                    thinker=self.name,
                    messages=chat_completion_messages,
                    prompt_name=SUMMARY_PROMPT,
                )[0]
            )  # TODO: do it safe

            summary_completion = completion.choices[0].message.content
            self.logger.info(
                f"📜 Evaluator {self.name} ({self.id}) summary: {summary_completion}"
            )
            self.logger.info(f"🔴 Evaluator {self.name} ({self.id}) is stopping...")
            self.is_end = True
            return

        if json_message_value["is_first"]:
            self.logger.info(
                f"📬 Evaluator {self.name} ({self.id}) preparing initial message..."
            )
            return

        chat_completion_messages = [
            {
                "role": "user",
                "content": f"METRICS: {json.dumps(metrics)}",
            },
            {
                "role": "user",
                "content": f"MEMORY: {message.value}",
            },
        ]

        completion = (
            spin(
                f"🧠 Evaluator {self.name} ({self.id}) is thinking...",
                lambda: self.llm.think(
                    thinker=self.name,
                    messages=chat_completion_messages,
                    prompt_name=METRICS_CALCULATOR_PROMPT,
                    schema=MetricCalculator,
                ),
            )
            if self.is_local_mode
            else self.llm.think(
                thinker=self.name,
                messages=chat_completion_messages,
                prompt_name=METRICS_CALCULATOR_PROMPT,
                schema=MetricCalculator,
            )[0]
        )  # TODO: do it safe

        metrics_update: MetricCalculator = completion.choices[0].message.parsed

        for metric in metrics_update.update:
            cache.metrics[metric.metric_name].value = metric.value

            #  TODO: make it safe and add more types like summary
            if cache.metrics[metric.metric_name].type == "counter":
                cache.metrics[metric.metric_name].collector_registry.labels(
                    simulation_id=self.simulation_id,
                    simulation_name=self.simulation_name,
                ).inc(
                    metric.value
                )  # TODO: fix misinterpretation of value (e.g. count vs gaugue...5 from LLM should be 1 always?)
            elif cache.metrics[metric.metric_name].type == "gauge":
                cache.metrics[metric.metric_name].collector_registry.labels(
                    simulation_id=self.simulation_id,
                    simulation_name=self.simulation_name,
                ).set(metric.value)
            elif cache.metrics[metric.metric_name].type == "histogram":
                cache.metrics[metric.metric_name].collector_registry.labels(
                    simulation_id=self.simulation_id,
                    simulation_name=self.simulation_name,
                ).observe(metric.value)
