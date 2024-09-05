import argparse
import tomllib

from autobox.schemas.config import LoggingConfig, ServerConfig
from autobox.schemas.simulation import (
    AgentConfig,
    LLMConfig,
    SimulationConfig,
    SimulationRequest,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Autobox")
    parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        default="config.toml",
        help="Path to the configuration file",
    )
    return parser.parse_args()


def load_simulation_config(file_path: str = "config.toml") -> SimulationRequest:
    with open(file_path, "rb") as f:
        config = tomllib.load(f)
        orchestrator = config.get("orchestrator", {})
        simulation_config = config.get("simulation", {})
        max_steps = simulation_config.get("max_steps", 0)
        timeout = simulation_config.get("timeout", 0)
        task = simulation_config.get("task", "")
        verbose = simulation_config.get("verbose", False)
        name = simulation_config.get("name", "")
        logging = simulation_config.get("logging", {})

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
                backstory=agent_config.get("backstory", ""),
                mailbox=agent_config.get("mailbox", {}),
                role=agent_config.get("role", ""),
            )
            agents.append(agent)

        simulation = SimulationConfig(
            name=name,
            max_steps=max_steps,
            timeout=timeout,
            task=task,
            verbose=verbose,
            logging=logging,
        )

        autobox_config = SimulationRequest(
            simulation=simulation,
            agents=agents,
            verbose=verbose,
            orchestrator=orchestrator,
        )

        return autobox_config


def load_server_config(file_path: str = "server.toml") -> ServerConfig:
    with open(file_path, "rb") as f:
        config = tomllib.load(f)
        server_config = config.get("server", {})
        logging_config = config.get("logging", {})
        logging = LoggingConfig(file_path=logging_config.get("file_path"))
        return ServerConfig(
            host=server_config.get("host", ""),
            port=server_config.get("port", 0),
            reload=server_config.get("reload", False),
            verbose=server_config.get("verbose", False),
            logging=logging,
        )
