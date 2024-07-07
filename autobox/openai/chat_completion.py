import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def create_chat_completion(messages):
    chat_completion = client.chat.completions.create(messages=messages, model="gpt-4o")
    return chat_completion.choices[0].message.content
