import tomllib


def load_config(path: str) -> dict:
    with open(f"{path}/agents.toml", "rb") as f:
        agents_config = tomllib.load(f)
    with open(f"{path}/tools.toml", "rb") as f:
        tools_config = tomllib.load(f)
    with open(f"{path}/autobox.toml", "rb") as f:
        autobox_config = tomllib.load(f)
    with open(f"{path}/tasks.toml", "rb") as f:
        tasks_config = tomllib.load(f)

    return {**agents_config, **tools_config, **autobox_config, **tasks_config}
