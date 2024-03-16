import json
from typing import Any, List, Literal

from pydantic import BaseModel

from src.llm.openai import LLM
from src.prompts.planner import PLANNER_PROMPT

PlanType = Literal["sequential", "consensual"]


class AgentStep(BaseModel):
    tool: str
    args: dict[str, Any]


class PlanStep(BaseModel):
    agent: str
    agent_id: int
    sub_task: str
    steps: List[AgentStep]


class Plan(BaseModel):
    steps: List[PlanStep]
    thinking_process: str
    end_condition: str
    type: str


class Planner:

    def __init__(self, model: str = None, context: dict = {}):
        self.llm = LLM(PLANNER_PROMPT, model=model)
        self.context = context

    def plan(self, task: str) -> Plan:
        message = self._get_message(task)
        response = self.llm.invoke(message)
        response = response.replace("```json", "").replace("```", "")
        data = json.loads(response)
        plan = Plan.parse_obj(data)
        return plan

    def _get_message(self, task: str):
        return f"""
        [AVAILABLE AGENTS]
        {self.context["agents"]}
        
        [AVAILABLES TOOLS]
        {self.context["tools"]}
        
        [TASK]
        {task}
        """
