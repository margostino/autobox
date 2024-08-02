import argparse
import asyncio

from autobox.core.simulator import prepare_simulation
from autobox.logger.logger import print_banner
from autobox.utils import load_config


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Autobox")
    parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        default="config.toml",
        help="Path to the configuration file",
    )

    args = parser.parse_args()

    print(f"Using configuration file: {args.config_file}")

    config = load_config(args.config_file)
    simulation = prepare_simulation(config)
    asyncio.run(simulation.run(timeout=300))


main()
