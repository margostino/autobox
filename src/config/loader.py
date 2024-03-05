import tomllib

from autobox.config.model import AgentConfig, LLMConfig, SimulationConfig, ToolConfig


def load_config() -> SimulationConfig:
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
        simulation_params = config.get("simulation", {})
        max_steps = simulation_params.get("max_steps", 0)
        initial_input = simulation_params.get("initial_input", "")
        entry_point = simulation_params.get("entry_point", "")

        agents_list = []
        for agent_data in config.get("agents", []):
            # Each agent may have its own llm configuration and tools
            llm_config = (
                LLMConfig(model=agent_data.get("llm", {}).get("model", ""))
                if "llm" in agent_data
                else None
            )

            tools = []
            for tool_data in agent_data.get("tools", []):
                tool = ToolConfig(
                    name=tool_data.get("name", ""),
                    type=tool_data.get("type", ""),
                    model=tool_data.get("model", ""),
                    description=tool_data.get("description", ""),
                    prompt_template=tool_data.get("prompt_template", ""),
                    input_description=tool_data.get("input_description", ""),
                )
                tools.append(tool)

            agent = AgentConfig(
                name=agent_data.get("name", ""),
                role=agent_data.get("role", ""),
                tools=tools,
                llm=llm_config,
                verbose=agent_data.get("verbose", False),
                system_message=agent_data.get("system_message", ""),
            )
            agents_list.append(agent)

        # Create the Simulation instance
        simulation = SimulationConfig(
            max_steps=max_steps,
            initial_input=initial_input,
            entry_point=entry_point,
            agents=agents_list,
        )

        return simulation
