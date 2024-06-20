"""Script to run the trained policy in the terminal."""
import argparse
import logging

import gymnasium as gym
import torch

import wandb
from moviebot.dialogue_manager.dialogue_policy import (
    A2CDialoguePolicy,
    DQNDialoguePolicy,
)
from moviebot.domain.movie_domain import MovieDomain
from reinforcement_learning.environment import DialogueEnvMovieBot
from reinforcement_learning.utils import define_possible_actions, get_config

logger = logging.getLogger(__name__)


def parse_args(args: str = None) -> argparse.Namespace:
    """Parses command line arguments.

    Args:
        args: String of arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(prog="run_dialogue_policy.py")
    parser.add_argument(
        "--agent-config",
        required=True,
        help="Path to the agent configuration file.",
    )
    parser.add_argument(
        "--artifact-name",
        required=True,
        help="W&B artifact name.",
    )
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to the model file in W&B.",
    )
    parser.add_argument(
        "--policy-type",
        required=True,
        help="Type of the policy, either 'dqn' or 'a2c'.",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args()

    logger.setLevel(logging.DEBUG)

    run = wandb.init()

    # Load agent config

    agent_config = get_config(args.agent_config, name="MovieBot").get()
    domain_path = agent_config.get("DATA", {}).get("domain_path")
    agent_domain = MovieDomain(domain_path) if domain_path else None
    agent_possible_actions = define_possible_actions(agent_domain)

    # Load the policy
    artifact = run.use_artifact(args.artifact_name, type="model")
    policy_artifact_filepath = artifact.get_path(args.model_path)
    policy_artifact_file = policy_artifact_filepath.download()

    if args.policy_type == "dqn":
        policy = DQNDialoguePolicy.load_policy(policy_artifact_file)
    elif args.policy_type == "a2c":
        policy = A2CDialoguePolicy.load_policy(policy_artifact_file)
    else:
        raise ValueError(
            f"Unknown policy type '{args.policy_type}'. "
            "Supported types are 'dqn' and 'a2c'."
        )

    # Create the environment
    env: DialogueEnvMovieBot = gym.make(
        "DialogueEnvMovieBot-v0",
        input_size=32,
        user_simulator_config=None,
        agent_config=agent_config,
        agent_possible_actions=agent_possible_actions,
        turn_penalty=0.0,
        b_use_intents=True,
    )

    # Run one conversation
    done = False
    observation, _ = env.reset()
    observation = torch.tensor([observation], dtype=torch.float)

    while not done:
        with torch.no_grad():
            action, _ = policy.select_action(observation)

        observation, reward, terminated, truncated, info = env.step(action)
        observation = torch.unsqueeze(observation, 0)
        done = terminated or truncated
        env.render()

    print(f"Reward: {reward}")
    env.close()
    run.finish()
