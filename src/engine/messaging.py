class Message:
    value: str
    from_agent_name: str = None
    from_agent_id: int = None

    def __init__(
        self, value: str, from_agent_id: int = None, from_agent_name: str = None
    ):
        self.value = value
        self.from_agent_name = from_agent_name
        self.from_agent_id = from_agent_id
