from autobox.api.get_projects import handle_get_projects


async def handle_get_project_by_id(project_id: str):
    projects = await handle_get_projects()
    project = [
        project for project in projects["projects"] if project["id"] == project_id
    ]
    # TODO: now is mocking project, until api supports projects management
    return project[0] if project else None
