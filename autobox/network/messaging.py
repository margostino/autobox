from asyncio import Queue


class Message:
    value: str
    # to_agent_id: int
    from_agent_id: int = None

    def __init__(self, value: str, from_agent_id: int = None):
        self.value = value
        # self.to_agent_id = to_agent_id
        self.from_agent_id = from_agent_id


class MessageBroker:
    mailbox: Queue

    def __init__(self):
        self.mailbox = Queue()
