import os
from typing import Any, Dict, List, Tuple, Union

from openai import NOT_GIVEN, OpenAI
from pydantic import BaseModel, Field

from autobox.schemas.constants import DEFAULT_PROMPT
from autobox.schemas.metrics import MetricCalculator


class LLM(BaseModel):
    model: str = Field(default="gpt-4o")
    system_prompts: Dict[str, str]
    parallel_tool_calls: bool = Field(default=NOT_GIVEN)
    tools: List[Dict] = None
    openai: OpenAI = None

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=4)

    def think(
        self,
        thinker: str,
        messages: List[Dict],  # TODO: create type
        prompt_name: str = DEFAULT_PROMPT,
        schema: Union[MetricCalculator] = None,
    ) -> Tuple[Any, bool, Union[str, None]]:
        completion_messages = [
            {"role": "system", "content": self.system_prompts[prompt_name]},
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
