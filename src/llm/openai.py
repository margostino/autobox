from openai import OpenAI

# from openai import OpenAI

# from openai.types.chat import ChatCompletion


class LLM:

    def __init__(self, system_prompt: str = None, model: str = None):
        self.client = OpenAI()
        self.model = model
        self.system_prompt = system_prompt

    # def bind_functions(self, functions):
    #     self.functions = functions

    def invoke(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message.content
