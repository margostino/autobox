from autobox.agents.prompts import PLANNER_PROMPT
from autobox.llm.openai import LLM


class Planner:

    def __init__(self, context={}):
        self.llm = LLM(PLANNER_PROMPT)
        self.context = context

    def plan(self, task: str) -> dict:
        message = self._get_message(task)
        print(f"Planner: {message}")
        return self.llm.invoke(message)

    def _get_message(self, task: str):
        return f"""
        [AVAILABLE AGENTS]
        {self.context["agents"]}
        
        [AVAILABLES TOOLS]
        {self.context["tools"]}
        
        [TASK]
        {task}
        """
