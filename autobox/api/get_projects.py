from autobox.api.get_simulations import handle_get_simulations
from autobox.transformations.project_simulations_to_response import transform


async def handle_get_projects():
    simulations = await handle_get_simulations()
    project_simulations = transform(simulations)
    # TODO: now is mocking project, until api supports projects management
    return {
        "projects": [
            {
                "id": "1",
                "name": "Friends dynamics",
                "description": "Experiment to understand how friends influence each other on decision making",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "2",
                "name": "Work dynamics",
                "description": "Experiment to understand how work environment influence productivity",
                "status": "active",
                "simulations": project_simulations,
            },
        ]
    }
