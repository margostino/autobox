import json

from autobox.core.agents.base import BaseAgent
from autobox.schemas.message import Message
from autobox.schemas.metrics import MetricCalculator
from autobox.utils.console import spin


class Evaluator(BaseAgent):
    # cache: Dict[str, Metric] = None

    # def set_cache(self, cache: Dict[str, Metric]):
    #     self.cache = cache

    async def handle_message(self, message: Message):
        from autobox.cache.cache import Cache

        cache = await Cache.simulation().get_simulation_status(self.simulation_id)
        json_message_value = json.loads(message.value)
        if json_message_value["is_first"]:
            self.logger.info(
                f"📬 Evaluator {self.name} ({self.id}) preparing initial message..."
            )
            return

        metrics = {
            name: metric.model_dump_json(exclude="collector_registry")
            for name, metric in cache.metrics.items()
        }
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

        completion = spin(
            f"🧠 Evaluator {self.name} ({self.id}) is thinking...",
            lambda: self.llm.think(
                self.name, chat_completion_messages, MetricCalculator
            ),
        )

        metrics_update: MetricCalculator = completion.choices[0].message.parsed

        for metric in metrics_update.update:
            cache.metrics[metric.metric_name].value = metric.value

            #  TODO: make it safe and add more types like summary
            if cache.metrics[metric.metric_name].type == "counter":
                cache.metrics[metric.metric_name].collector_registry.inc(
                    metric.value
                )  # TODO: fix misinterpretation of value (e.g. 5 from LLM should be 1 always?)
            elif cache.metrics[metric.metric_name].type == "gauge":
                cache.metrics[metric.metric_name].collector_registry.set(metric.value)
            elif cache.metrics[metric.metric_name].type == "histogram":
                cache.metrics[metric.metric_name].collector_registry.observe(
                    metric.value
                )
