from typing import Dict

from openai import OpenAI

# from openai.types.chat import ChatCompletion


class LLM:
    client: OpenAI

    def __init__(self):
        self.client = OpenAI(model="gpt-4-turbo-preview")

    # def bind_functions(self, functions):
    #     self.functions = functions

    def invoke(self, message: str) -> Dict:
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
        )
        print(response)
        return {}
        # print(response.choices[0].message)

        # response = self.llm.complete(
        #     prompt=message.value,
        #     max_tokens=100,
        #     temperature=0.7,
        #     top_p=1.0,
        #     frequency_penalty=0.0,
        #     presence_penalty=0.0,
        #     stop=["\n"],
        # )
