from typing import List


def get_tools(agent_names: List[str]):
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thinking_process": {
                            "type": "string",
                            "description": f"Explain step-by-step why the decision-making process requires ${name} intervention.",
                        },
                        "task_status": {
                            "type": "string",
                            "description": "A summary of the final task status based on all agents' contributions. Max 50 words.",
                        },
                        "instruction": {
                            "type": "string",
                            "description": f"Instructions for the ${name} agent to follow. Max 50 words.",
                        },
                    },
                    "required": ["thinking_process", "task_status", "instruction"],
                },
                "description": f"Call this function when you need to a collaboration and contribution from ${name}.",
            },
        }
        for name in agent_names
    ]
