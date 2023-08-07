"""Run MovieBot.

This module is the entry point of the MovieBot application. It parses the
command line arguments and loads the configuration file. It then instantiates
the appropriate controller and executes the agent.


Usage: python -m moviebot.run -c <path_to_config.yaml>

Version: Python 3.9
"""

import argparse
import logging

import confuse

from moviebot.controller import server_rest, server_socket
from moviebot.controller.controller_telegram import ControllerTelegram
from moviebot.controller.controller_terminal import ControllerTerminal
from moviebot.database.db_users import UserDB

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-12s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()

_DEFAULT_CONFIG = "config/moviebot_config.yaml"


def parse_args(args: str = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args (optional): List of arguments to parse. If not provided, uses
            sys.argv[1:]. Defaults to None.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="MovieBot: A conversational agent for movie recommendations"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to the configuration file",
        default=_DEFAULT_CONFIG,
    )
    return parser.parse_args(args)


def get_config(path: str) -> confuse.Configuration:
    config = confuse.Configuration("MovieBot", __name__)
    config.set_file(path)
    logger.info(f'Configuration file "{path}" is loaded.')
    return config


def init_db():
    """Initializes the user database."""
    UserDB().setup_db()


if __name__ == "__main__":
    args = parse_args()
    config = get_config(args.config)
    if config["DEBUG"].get(False):
        logger.setLevel(logging.DEBUG)

    init_db()
    if config["TELEGRAM"].get(False):
        CONTROLLER = ControllerTelegram()
        CONTROLLER.execute_agent(config.get())
    elif config["FLASK_SOCKET"].get(False):
        server_socket.run(config.get())
    elif config["FLASK_REST"].get(False):
        server_rest.run(config.get())
    else:
        CONTROLLER = ControllerTerminal(config.get())
        CONTROLLER.execute_agent()
