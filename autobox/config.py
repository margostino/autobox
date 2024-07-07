import tomllib

from autobox.schemas.simulation import AgentConfig, LLMConfig, SimulationConfig


def load_config(file_path: str) -> SimulationConfig:
    with open(file_path, "rb") as f:
        config = tomllib.load(f)
        simulation_params = config.get("simulation", {})
        max_steps = simulation_params.get("max_steps", 0)
        task = simulation_params.get("task", "")

        agents = []
        for agent_data in config.get("agents", []):
            llm_config = (
                LLMConfig(model=agent_data.get("llm", {}).get("model", ""))
                if "llm" in agent_data
                else None
            )

            agent = AgentConfig(
                name=agent_data.get("name", ""),
                llm=llm_config,
                verbose=agent_data.get("verbose", False),
                backstory=agent_data.get("backstory", ""),
            )
            agents.append(agent)

        simulation = SimulationConfig(
            max_steps=max_steps,
            task=task,
            agents=agents,
        )

        return simulation
