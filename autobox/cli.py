import asyncio

from autobox.common.logger import print_banner
from autobox.core.bootstrap import prepare_simulation
from autobox.utils.config import load_simulation_config, parse_args


def main():
    print_banner()
    args = parse_args()

    print(f"Using configuration file: {args.config_file}")

    config = load_simulation_config(args.config_file)
    simulation = prepare_simulation(config)
    asyncio.run(simulation.run())


main()
