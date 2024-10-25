from autobox.api.get_projects import handle_get_projects


async def handle_get_organizations():
    projects = await handle_get_projects()
    # TODO: now is mocking project, until api supports projects management
    return {
        "organizations": [
            {
                "id": "1",
                "name": "Darma",
                "description": "",
                "projects": projects["projects"],
            },
            {
                "id": "2",
                "name": "Acme",
                "description": "",
                "projects": projects["projects"],
            },
            {
                "id": "3",
                "name": "Marvel",
                "description": "",
                "projects": projects["projects"],
            },
            {
                "id": "4",
                "name": "DC",
                "description": "",
                "projects": projects["projects"],
            },
            {
                "id": "5",
                "name": "Mars",
                "description": "",
                "projects": projects["projects"],
            },
        ]
    }
