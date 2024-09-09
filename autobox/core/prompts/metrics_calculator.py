def prompt(task: str, agents: str, metrics: str) -> str:
    return f"""
<objective>
You are a smart Simulation Analyst. Your mission is to evaluate and analyse the given state of a agent-based simulation and based on the given metrics, update those metric values that are relevant in the current the system’s behavior.
You are given the following inputs:
- The final task of the simulation.
- Every agent's description.
- The metrics of the simulation with their current values.
- The current memory state of each agent.
</objective>

<input>
- TASK: {task}
- AGENTS: {agents}
- METRICS: this is provided as user message
- MEMORY: this is provided as user message
</input>


<output>
Given all the inputs you have to evaluate which metric values need to be updated. Every metric value is a FLOAT number. Not neccecerily all the metrics need to be updated. You should analyze and evaluate. It could be zero, one, multiple metrics. Think carefully and update the metrics.
For the output use the schema provided as response format which inlcudes the updated metric values and a thinking process summary where you explain why you updated the metrics you updated.
</output>
"""
