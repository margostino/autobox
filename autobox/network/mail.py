class Message:
    value: str
    to_agent_id: int
    from_agent_id: int = None

    def __init__(self, to_agent_id: int, value: str, from_agent_id: int = None):
        self.to_agent_id = to_agent_id
        self.value = value
        self.from_agent_id = from_agent_id
