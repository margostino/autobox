from autobox.api.get_simulations import handle_get_simulations


async def handle_get_projects():
    simulations = await handle_get_simulations()
    # TODO: now is mocking project, until api supports projects management
    return {
        "projects": [
            {
                "id": "1",
                "name": "Demo",
                "description": "Demo project",
                "status": "active",
                "simulations": simulations,
            },
            {
                "id": "2",
                "name": "Demo2",
                "description": "Demo2 project",
                "status": "active",
                "simulations": simulations,
            },
        ]
    }
