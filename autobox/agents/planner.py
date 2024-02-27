from autobox.agents.prompts import PLANNER_PROMPT
from autobox.llm.openai import LLM


class Planner:

    def __init__(self):
        self.llm = LLM()
        self.prompt = PLANNER_PROMPT

    def plan(self, task: str) -> dict:
        return f"Planner: {task}"
