from typing import List

from pydantic import BaseModel


class MailboxConfig(BaseModel):
    max_size: int


class LLMConfig(BaseModel):
    model: str


class AgentConfig(BaseModel):
    name: str
    verbose: bool
    backstory: str
    llm: LLMConfig
    mailbox: MailboxConfig


class OrchestratorConfig(BaseModel):
    name: str
    mailbox: MailboxConfig


class SimulationConfig(BaseModel):
    max_steps: int
    timeout: int
    task: str


class SimulationRequest(BaseModel):
    simulation: SimulationConfig
    orchestrator: OrchestratorConfig
    agents: List[AgentConfig]
