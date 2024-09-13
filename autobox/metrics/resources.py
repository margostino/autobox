import docker

from autobox.common.logger import Logger


def start_grafana_container():
    logger = Logger.get_instance()
    client = docker.from_env()

    logger.info("Checking if Grafana container is already running...")

    try:
        container = client.containers.get("grafana")

        if container.status == "running":
            logger.info(
                f"Grafana container is already running with ID: {container.short_id}"
            )
            return container
        else:
            logger.info("Grafana container exists but is not running. Starting it...")
            container.start()
            logger.info(f"Grafana container started with ID: {container.short_id}")
            return container

    except docker.errors.NotFound:
        logger.info(
            "Grafana container not found. Pulling the image and starting a new one..."
        )

        # Pull the Grafana image and start a new container
        client.images.pull("grafana/grafana")

        container = client.containers.run(
            "grafana/grafana",
            detach=True,
            ports={"3000/tcp": 3000},
            name="grafana",
        )

        logger.info(f"Grafana container started with ID: {container.short_id}")
        return container
