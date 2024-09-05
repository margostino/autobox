import asyncio
import os
import time

from openai import OpenAI
from pydantic import BaseModel, Field

from autobox.core import llm
from autobox.core.network import Network
from autobox.core.prompts.metrics_definition import prompt
from autobox.schemas.metrics import Metrics
from autobox.utils.console import blue, green, yellow

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=4)


class Simulation(BaseModel):
    network: Network
    timeout: int = Field(default=120)
    llm

    async def run(self):
        print(f"{green('✅ Autobox is running')}")
        start_time = time.time()

        task = asyncio.create_task(self.network.run())

        try:
            await asyncio.wait_for(task, timeout=self.timeout)
        except asyncio.TimeoutError:
            print(f"{yellow('Simulation ended due to timeout.')}")
        finally:
            self.network.stop()
            print(f"{blue('🔚 Simulation finished.')}")

        elapsed_time = int(time.time() - start_time)
        print(f"{blue(f"⏱️ Elapsed time: {elapsed_time} seconds.")}")

    def abort(self):
        self.network.stop()
        print(f"{blue('🔚 Simulation aborted.')}")

    def plan(self):
        print(f"{blue('Planning Simulation...')}")

        completion_messages = [
            {"role": "system", "content": prompt()},
            {"role": "user", "content": f"Simulation TASK: {self.network.orchestrator.task}"},
        ]

        completion = openai.beta.chat.completions.parse(
            messages=completion_messages,
            model="gpt-4o-2024-08-06",
            temperature=0,
            response_format=Metrics,
            # response_format=list[Metric]
        )
        metrics = completion.choices[0].message.parsed


