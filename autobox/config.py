import tomllib

from autobox.schemas.simulation_request import (
    AgentConfig,
    LLMConfig,
    SimulationConfig,
    SimulationRequest,
)


def load_config(file_path: str) -> SimulationRequest:
    with open(file_path, "rb") as f:
        config = tomllib.load(f)
        orchestrator = config.get("orchestrator", {})
        simulation_config = config.get("simulation", {})
        max_steps = simulation_config.get("max_steps", 0)
        timeout = simulation_config.get("timeout", 0)
        task = simulation_config.get("task", "")

        agents = []
        for agent_config in config.get("agents", []):
            llm_config = (
                LLMConfig(model=agent_config.get("llm", {}).get("model", ""))
                if "llm" in agent_config
                else None
            )

            agent = AgentConfig(
                name=agent_config.get("name", ""),
                llm=llm_config,
                verbose=agent_config.get("verbose", False),
                backstory=agent_config.get("backstory", ""),
                mailbox=agent_config.get("mailbox", {}),
            )
            agents.append(agent)

        simulation = SimulationConfig(max_steps=max_steps, timeout=timeout, task=task)

        autobox_config = SimulationRequest(
            simulation=simulation,
            agents=agents,
            orchestrator=orchestrator,
        )

        return autobox_config
