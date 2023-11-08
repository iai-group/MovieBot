"""Main script for running reinforcement learning algorithms to learn
MovieBot's dialogue policy.

Logging and training monitoring is done using Weight and Biases (wandb)."""

import argparse
import logging

import confuse

from reinforcement_learning.training.trainer_a2c import TrainerA2C
from reinforcement_learning.training.trainer_dqn import TrainerDQN
from reinforcement_learning.utils import get_config

DEFAUTL_RL_CONFIG = "reinforcement_learning/config/train_dqn_policy.yaml"


def parse_args(args: str = None) -> argparse.Namespace:
    """Parses command line arguments.

    Args:
        args: String of arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(prog="train_dialogue_policy.py")
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAUTL_RL_CONFIG,
        help="Path to the configuration file.",
    )
    participants_group = parser.add_argument_group("Participants")
    participants_group.add_argument(
        "--usersim_config",
        help="Path to the user simulator configuration file.",
    )
    participants_group.add_argument(
        "--agent_config",
        help="Path to the agent configuration file.",
    )
    model_group = parser.add_argument_group("Model")
    model_group.add_argument(
        "--model_type",
        type=str,
        help="Type of the model.",
        dest="model.model_type",
    )
    model_group.add_argument(
        "--policy_input_size",
        type=int,
        help="Size of the input vector.",
        dest="model.policy_input_size",
    )
    model_group.add_argument(
        "--hidden_size",
        type=int,
        help="Size of the hidden layer.",
        dest="model.hidden_size",
    )
    model_group.add_argument(
        "--model_path",
        type=str,
        help="Path to the model.",
        dest="model.model_path",
    )
    run_options_group = parser.add_argument_group("Run options")
    run_options_group.add_argument(
        "--use_intents",
        action="store_true",
        help="Whether or not to include intents in the state representation.",
    )
    run_options_group.add_argument(
        "--no_nlu",
        action="store_true",
        help="Whether or not to use NLU.",
    )
    run_options_group.add_argument(
        "--turn_penalty",
        type=float,
        help="Penalty for each turn.",
    )
    dqn_hyperparameters_group = parser.add_argument_group("DQN Hyperparameters")
    dqn_hyperparameters_group.add_argument(
        "--batch_size",
        type=int,
        help="Batch size.",
        dest="hyperparams.batch_size",
    )
    dqn_hyperparameters_group.add_argument(
        "--dqn-gamma",
        type=float,
        help="Discount factor.",
        dest="hyperparams.gamma",
    )
    dqn_hyperparameters_group.add_argument(
        "--eps_start",
        type=float,
        help="Starting value of epsilon.",
        dest="hyperparams.eps_start",
    )
    dqn_hyperparameters_group.add_argument(
        "--eps_end",
        type=float,
        help="Ending value of epsilon.",
        dest="hyperparams.eps_end",
    )
    dqn_hyperparameters_group.add_argument(
        "--eps_decay",
        type=float,
        help="Epsilon decay.",
        dest="hyperparams.eps_decay",
    )
    dqn_hyperparameters_group.add_argument(
        "--n_episodes",
        type=int,
        help="Number of episodes.",
        dest="hyperparams.n_episodes",
    )
    dqn_hyperparameters_group.add_argument(
        "--tau",
        type=float,
        help="Soft update factor tau.",
        dest="hyperparams.tau",
    )
    dqn_hyperparameters_group.add_argument(
        "--learning_rate",
        type=float,
        help="Learning rate.",
        dest="hyperparams.learning_rate",
    )
    dqn_hyperparameters_group.add_argument(
        "--replay_memory_size",
        type=int,
        help="Replay memory size.",
        dest="hyperparams.replay_memory_size",
    )
    a2c_hyperparameters_group = parser.add_argument_group("A2C Hyperparameters")
    a2c_hyperparameters_group.add_argument(
        "--n_envs",
        type=int,
        help="Number of environments.",
        dest="hyperparams.n_envs",
    )
    a2c_hyperparameters_group.add_argument(
        "--n_updates",
        type=int,
        help="Number of updates.",
        dest="hyperparams.n_updates",
    )
    a2c_hyperparameters_group.add_argument(
        "--n_steps_per_update",
        type=int,
        help="Number of steps per update.",
        dest="hyperparams.n_steps_per_update",
    )
    a2c_hyperparameters_group.add_argument(
        "--a2c-gamma",
        type=float,
        help="Discount factor.",
        dest="hyperparams.gamma",
    )
    a2c_hyperparameters_group.add_argument(
        "--lambda",
        type=float,
        help="Lambda for generalized advantage estimation.",
        dest="hyperparams.lambda",
    )
    a2c_hyperparameters_group.add_argument(
        "--ent_coef",
        type=float,
        help="Entropy coefficient.",
        dest="hyperparams.ent_coef",
    )
    return parser.parse_args(args)


def load_config(args: argparse.Namespace) -> confuse.Configuration:
    """Loads config from file and command line arguments.

    Args:
        args: Command line arguments.

    Returns:
        Configuration.
    """
    config = get_config(args.config, "MovieBot RL Training")
    config.set_args(args, dots=True)
    return config


if __name__ == "__main__":
    args = parse_args()
    config = load_config(args)

    if config["debug"].get():
        logging.basicConfig(level=logging.DEBUG)

    # Create trainer
    algorithm = config["model"]["algorithm"].get()
    if algorithm == "dqn":
        trainer = TrainerDQN(config)
    elif algorithm == "a2c":
        trainer = TrainerA2C(config)
    else:
        raise ValueError(f"Algorithm {algorithm} is not supported.")

    # Train policy
    trainer.train_policy()
