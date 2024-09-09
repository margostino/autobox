import os
from typing import Any, Dict, List, Tuple, Union

from openai import NOT_GIVEN, OpenAI


class LLM:
    model: str
    system_prompt: str
    tools: List[Dict]
    openai: "OpenAI"
    parallel_tool_calls: bool

    def __init__(
        self,
        system_prompt: str,
        tools: List[Dict] = None,
        model: str = "gpt-4o-2024-08-06",
        parallel_tool_calls: bool = NOT_GIVEN,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=4)
        self.parallel_tool_calls = parallel_tool_calls

    def think(
        self, thinker, messages, schema=None
    ) -> Tuple[Any, bool, Union[str, None]]:
        completion_messages = [
            {"role": "system", "content": self.system_prompt},
        ] + messages

        if schema:
            completion = self.openai.beta.chat.completions.parse(
                messages=completion_messages,
                model=self.model,
                temperature=0,
                response_format=schema,
            )
        else:
            completion = self.openai.chat.completions.create(
                messages=completion_messages,
                model=self.model,
                parallel_tool_calls=self.parallel_tool_calls,
                temperature=0,
                tools=self.tools,
            )

        return (completion, True, f"{thinker} knows what to do!")
