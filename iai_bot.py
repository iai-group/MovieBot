"""This code is executed to run IAI MovieBot"""

__author__ = "Javeria Habib"

import os
import sys

import yaml

from iaibot.controller.controller_bot import ControllerBot
from iaibot.controller.controller_terminal import ControllerTerminal


def _validate_file(file_name, file_type):
    """Checks if the file is valid and is present

    :param file_name: name/path of the file provided
    :param file_type: the type/extension of the file
    :return: error and details
    """
    if isinstance(file_name, str):
        if os.path.isfile(file_name):
            details = file_name.split('.')
            if len(details) > 1:
                if details[-1] == file_type:
                    return 'NoError'
                else:
                    return 'ValueErrorType:{}'.format(details[-1])
            else:
                return 'ValueErrorType:{}'.format(details[-1])
        else:
            return 'FileNotFoundError'
    else:
        return 'ValueError'


def arg_parse(args=None):
    """ Parses the arguments in the configuration file

    :param args: configuration file for the dialogue
    :return: a dictionary containing the settings in the configuration file and a boolean
    variable identifying if the conversation is in Telegram
    """
    argv = args if args else sys.argv
    cfg_parser = None

    if len(argv) < 3:
        print('WARNING: Configuration file is not provided.')
        config_file = r'data_and_config/config/moviebot_config.yaml'
        print(f'Default configuration file selected is \'{config_file}\'')
    else:
        config_file = argv[2]
    file_val = _validate_file(config_file, 'yaml')
    if file_val == 'NoError':
        with open(config_file, 'r') as file:
            cfg_parser = yaml.load(file, Loader=yaml.Loader)
    elif file_val == 'ValueError':
        raise ValueError('Unacceptable type of configuration file name')
    elif file_val == 'FileNotFoundError':
        raise FileNotFoundError('Configuration file {} not found'.format(config_file))
    elif file_val.startswith('ValueErrorType'):
        raise ValueError(f'Unknown file type {file_val.split(":")[-1]} for configuration file')

    if cfg_parser:
        print(f'Configuration file "{config_file}" is loaded.')
        return cfg_parser, cfg_parser['BOT']
    else:
        raise ValueError('The configuration file does not contain the correct format.')


if __name__ == '__main__':
    # Usage: python iai_bot.py -c <path_to_config.yaml>
    # Version: Python 3.6
    CONFIGURATION, BOT = arg_parse()
    if BOT:
        CONTROLLER = ControllerBot()
    else:
        CONTROLLER = ControllerTerminal()
    CONTROLLER.execute_agent(CONFIGURATION)
