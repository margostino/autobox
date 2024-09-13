import asyncio
import sys

from autobox.cache.cache import Cache
from autobox.cli import run_local_simulation
from autobox.common.logger import Logger, print_banner
from autobox.metrics.resources import start_grafana_container
from autobox.server import start_server
from autobox.utils.config import load_server_config, load_simulation_config, parse_args


async def main():
    print_banner()

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

    logger.info(f"Using configuration file ({mode} mode): {args.config_file}")

    container = start_grafana_container()

    Cache.init()

    if mode == "local":
        await run_local_simulation(config)
    elif mode == "server":
        start_server(config)
    else:
        logger.error(f"Invalid mode specified: {mode}. Use 'local' or 'server'.")
        sys.exit(1)

    container.stop()
    container.remove()


if __name__ == "__main__":
    asyncio.run(main())
