import asyncio
import sys

from autobox.cache.cache import Cache
from autobox.cli import run_local_simulation
from autobox.common.logger import Logger
from autobox.metrics.resources import start_grafana_and_prometheus_containers
from autobox.server import start_server
from autobox.utils.config import load_server_config, load_simulation_config, parse_args


async def main():
    args = parse_args()
    mode = args.mode

    config = (
        load_simulation_config(args.config_file)
        if mode == "local"
        else load_server_config(args.config_file)
    )

    logger = Logger(
        name=mode, verbose=config.logging.verbose, log_path=config.logging.file_path
    )

    logger.print_banner()

    logger.info(f"Using configuration file ({mode} mode): {args.config_file}")

    grafana_container, prometheus_container = start_grafana_and_prometheus_containers()

    Cache.init()

    if mode == "local":
        await run_local_simulation(config)
    elif mode == "server":
        start_server(config)
    else:
        logger.error(f"Invalid mode specified: {mode}. Use 'local' or 'server'.")
        sys.exit(1)

    # TODO: parallelize and centralize cleanup resources
    grafana_container.stop()
    grafana_container.remove()
    prometheus_container.stop()
    prometheus_container.remove()


if __name__ == "__main__":
    asyncio.run(main())
