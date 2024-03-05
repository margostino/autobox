from typing import Dict

from openai import OpenAI

# from openai import OpenAI

# from openai.types.chat import ChatCompletion


class LLM:

    def __init__(self, system_prompt: str = None):
        self.client = OpenAI()
        self.system_prompt = system_prompt

    # def bind_functions(self, functions):
    #     self.functions = functions

    def invoke(self, message: str) -> Dict:
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
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
