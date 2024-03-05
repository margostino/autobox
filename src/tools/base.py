class BaseTool:

    def __init__(self, name: str, description: str = None, parameters: dict = {}):
        self.name = name
        self.description = description
        self.parameters = parameters

    async def async_handle(self):
        print("Handling message")

    def handle(self):
        print("Handling message")

    def get_tool_profile(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
