from typing import Callable


class BaseTool:

    def __init__(
        self,
        name: str,
        description: str = None,
        parameters: dict = {},
        function: Callable = None,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

    async def async_handle(self):
        print("Handling message")

    def handle(self):
        print("Handling message")

    def to_prompt(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
