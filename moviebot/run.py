import logging
import os
import sys

import yaml

from moviebot.controller import server_rest, server_socket
from moviebot.controller.controller_telegram import ControllerTelegram
from moviebot.controller.controller_terminal import ControllerTerminal

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-12s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()

_DEFAULT_CONFIG = "config/moviebot_config.yaml"


def _validate_file(file_name, file_type):
    """Checks if the file is valid and is present

    Args:
      file_name: name/path of the file provided
      file_type: the type/extension of the file

    Returns:
      error and details

    """
    if isinstance(file_name, str):
        if os.path.isfile(file_name):
            details = file_name.split(".")
            if len(details) > 1:
                if details[-1] == file_type:
                    return "NoError"
                else:
                    return "ValueErrorType:{}".format(details[-1])
            else:
                return "ValueErrorType:{}".format(details[-1])
        else:
            return "FileNotFoundError"
    else:
        return "ValueError"


def arg_parse(args=None):
    """Parses the arguments in the configuration file

    Args:
      args: configuration file for the dialogue (Default value = None)

    Returns:
      a dictionary containing the settings in the configuration file and a
      boolean variable identifying if the conversation is in Telegram.

    """
    argv = args if args else sys.argv
    cfg_parser = None
    if len(argv) < 3:
        config_file = _DEFAULT_CONFIG
        logger.warning("Configuration file is not provided.")
        logger.warning(
            f"Default configuration file selected is '{config_file}'"
        )
    else:
        config_file = argv[2]
    file_val = _validate_file(config_file, "yaml")
    if file_val == "NoError":
        with open(config_file, "r") as file:
            cfg_parser = yaml.load(file, Loader=yaml.Loader)
    elif file_val == "ValueError":
        raise ValueError("Unacceptable type of configuration file name")
    elif file_val == "FileNotFoundError":
        raise FileNotFoundError(
            "Configuration file {} not found".format(config_file)
        )
    elif file_val.startswith("ValueErrorType"):
        file_type = file_val.split(":")[-1]
        raise ValueError(
            f"Unknown file type {file_type} for configuration file"
        )

    if cfg_parser:
        logger.info(f'Configuration file "{config_file}" is loaded.')
        return (
            cfg_parser,
            cfg_parser["TELEGRAM"],
            cfg_parser["POLLING"],
            cfg_parser["FLASK"],
        )
    else:
        raise ValueError(
            "The configuration file does not contain the correct format."
        )


def get_config():
    configuration, _, _ = arg_parse()
    return configuration


if __name__ == "__main__":
    # Usage: python -m  moviebot.run -c <path_to_config.yaml>
    # Version: Python 3.10
    CONFIGURATION, BOT, POLLING, FLASK = arg_parse()
    if CONFIGURATION["DEBUG"]:
        logger.setLevel(logging.DEBUG)
    if BOT:
        if POLLING:
            CONTROLLER = ControllerTelegram()
            CONTROLLER.execute_agent(CONFIGURATION)
    elif FLASK:
        server_rest.run(CONFIGURATION)
    else:
        CONTROLLER = ControllerTerminal(CONFIGURATION)
        CONTROLLER.execute_agent()
