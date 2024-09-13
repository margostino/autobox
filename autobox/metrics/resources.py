import os

import docker
from autobox.common.logger import Logger


def create_network_if_not_exists(network_name: str):
    client = docker.from_env()
    logger = Logger.get_instance()
    try:
        client.networks.get(network_name)
        logger.info(f"Network {network_name} already exists.")
    except docker.errors.NotFound:
        logger.info(f"Network {network_name} not found. Creating it...")
        client.networks.create(network_name, driver="bridge")
        logger.info(f"Network {network_name} created.")


def start_container(
    name: str,
    image: str,
    ports: dict,
    volumes: dict = None,
    environment: dict = None,
    command: list = None,
    network: str = "internal",
):
    logger = Logger.get_instance()
    client = docker.from_env()

    create_network_if_not_exists(network)

    logger.info(f"Checking if {name.capitalize()} container is already running...")

    try:
        container = client.containers.get(name)

        if container.status == "running":
            logger.info(
                f"{name.capitalize()} container is already running with ID: {container.short_id}"
            )
            return container
        else:
            logger.info(
                f"{name.capitalize()} container exists but is not running. Starting it..."
            )
            container.start()
            logger.info(
                f"{name.capitalize()} container started with ID: {container.short_id}"
            )
            return container

    except docker.errors.NotFound:
        logger.info(
            f"{name.capitalize()} container not found. Pulling the image and starting a new one..."
        )

        client.images.pull(image)

        container = client.containers.run(
            image,
            detach=True,
            ports=ports,
            name=name,
            restart_policy={"Name": "always"},
            volumes=volumes,
            environment=environment,
            command=command,
            extra_hosts={"host.docker.internal": "host-gateway"},
            network=network,
        )

        logger.info(
            f"{name.capitalize()} container started with ID: {container.short_id}"
        )
        return container


# TODO: from config?
def start_grafana_container():
    grafana_datasource_path = os.path.abspath(
        "./docker/grafana/datasources/datasources.yml"
    )

    return start_container(
        name="grafana",
        image="grafana/grafana",
        ports={"3000/tcp": 3000},
        environment={
            "GF_SECURITY_ADMIN_USER": "admin",
            "GF_SECURITY_ADMIN_PASSWORD": "admin",
            "GF_AUTH_ANONYMOUS_ENABLED": "true",
            "GF_AUTH_ANONYMOUS_ORG_ROLE": "Admin",
            "GF_SECURITY_DISABLE_INITIAL_ADMIN_CREATION": "true",
            "GF_AUTH_DISABLE_LOGIN_FORM": "true",
        },
        volumes={
            "grafana_data": {"bind": "/var/lib/grafana", "mode": "rw"},
            grafana_datasource_path: {
                "bind": "/etc/grafana/provisioning/datasources/datasources.yml",
                "mode": "rw",
            },
        },
    )


# TODO: from config?
def start_prometheus_container():
    prometheus_config_path = os.path.abspath("./docker/prometheus/prometheus.yml")
    return start_container(
        name="prometheus",
        image="prom/prometheus",
        ports={"9090/tcp": 9090},
        volumes={
            prometheus_config_path: {
                "bind": "/etc/prometheus/prometheus.yml",
                "mode": "rw",
            },
        },
        command=["--config.file=/etc/prometheus/prometheus.yml"],
    )


def start_grafana_and_prometheus_containers():
    # TODO: parallelize
    prometheus_container = start_prometheus_container()
    grafana_container = start_grafana_container()
    return grafana_container, prometheus_container
