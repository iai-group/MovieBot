"""Trainer for Advantage Actor Critic (A2C)."""

import logging
from collections import Counter

import confuse
import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import torch

import wandb
from moviebot.dialogue_manager.dialogue_policy import A2CDialoguePolicy
from reinforcement_learning.training.trainer import Trainer


class TrainerA2C(Trainer):
    def __init__(self, config: confuse.Configuration) -> None:
        """Initializes the trainer.

        Args:
            config: Training configuration.
        """
        super().__init__(config)
        self.num_episodes = self.config["hyperparams"]["n_episodes"].get()
        self.n_envs = self.config["hyperparams"]["n_envs"].get()

    def initialize_policy(self) -> None:
        """Initializes the policy."""
        policy_input_size = self.config["model"]["policy_input_size"].get()
        hidden_size = self.config["model"]["hidden_size"].get()
        output_size = len(self.agent_possible_actions)

        self.policy = A2CDialoguePolicy(
            policy_input_size,
            hidden_size,
            output_size,
            self.agent_possible_actions,
            num_timesteps=self.num_episodes,
            n_envs=self.n_envs,
        )

        wandb.watch(self.policy.actor)
        wandb.watch(self.policy.critic)

    def train_episode(
        self,
        episode: int,
        n_steps_per_episode: int,
        gamma: float,
        lambda_gae: float,
        entropy_coef: float,
    ) -> None:
        """Trains the policy for one episode.

        Args:
            episode: Episode number.
            n_steps_per_episode: Number of steps per episode.
            gamma: Discount factor.
            lambda_gae: Lambda for generalized advantage estimation.
            entropy_coef: Entropy coefficient.
        """
        # Reset lists that collect experiences of an episode
        episode_value_preds = torch.zeros(n_steps_per_episode, self.n_envs)
        episode_rewards = torch.zeros(n_steps_per_episode, self.n_envs)
        episode_action_log_probs = torch.zeros(n_steps_per_episode, self.n_envs)
        masks = torch.ones(n_steps_per_episode, self.n_envs)

        # Reset the environments (only for the first episode)
        if episode == 0:
            states, _ = self.envs_wrapper.reset()

        # Play n steps in parallel for data collection
        for step in range(n_steps_per_episode):
            states = torch.squeeze(torch.Tensor(states))
            # Select actions using current states
            (
                actions,
                action_log_probs,
                values,
                entropy,
            ) = self.policy.select_action(states)

            # Perform actions in the environment to get next states and rewards
            (
                states,
                rewards,
                terminated,
                truncated,
                infos,
            ) = self.envs_wrapper.step(actions.cpu().numpy())

            # Count the number of truncations
            self.num_truncations += truncated.sum().item()

            # Store experiences
            episode_value_preds[step] = torch.squeeze(values)
            episode_rewards[step] = torch.Tensor(rewards)
            episode_action_log_probs[step] = action_log_probs

            # Store success information
            for info in infos.get("final_info", []):
                if info is not None and "success" in info:
                    self.episodes_success.append(info["success"])
                    wandb.log(
                        {
                            "success": int(info["success"]),
                            "reward": info["reward"],
                        }
                    )

            # Update masks
            masks[step] = torch.Tensor(
                [not is_terminated for is_terminated in terminated]
            )

        # Compute the losses
        critic_loss, actor_loss = self.policy.get_losses(
            episode_rewards,
            episode_action_log_probs,
            episode_value_preds,
            entropy,
            masks,
            gamma,
            lambda_gae,
            entropy_coef,
        )

        # Update the policy
        self.policy.update_parameters(critic_loss, actor_loss)

        # Store losses and entropies
        self.critic_losses.append(critic_loss.item())
        self.actor_losses.append(actor_loss.item())
        self.entropies.append(entropy.mean().item())

        wandb.log(
            {
                "Critic Loss": critic_loss.item(),
                "Actor Loss": actor_loss.item(),
                "Entropy": entropy.mean().item(),
            }
        )

    def train_policy(self) -> None:
        """Trains the policy."""
        # Create the environment
        envs = self.create_environment(b_vectorized=True)
        # Wrapper to save episode returns and lengths
        self.envs_wrapper = gym.wrappers.RecordEpisodeStatistics(
            envs,
            deque_size=self.n_envs * self.num_episodes,
            num_envs=self.n_envs,
            is_vector_env=True,
        )

        # Get training parameters
        self.hyperparameters = self.config["hyperparams"].get()
        self.n_steps_per_episode = self.hyperparameters.get(
            "n_steps_per_episode"
        )
        gamma = self.hyperparameters.get("gamma")
        lambda_gae = self.hyperparameters.get("lambda")
        entropy_coef = self.hyperparameters.get("ent_coef")

        self.critic_losses = []
        self.actor_losses = []
        self.entropies = []
        self.episodes_success = []
        self.num_truncations = 0

        for episode in range(self.num_episodes):
            logging.info(f"Episode {episode + 1}/{self.num_episodes}")
            # Train for one episode
            self.train_episode(
                episode,
                self.n_steps_per_episode,
                gamma,
                lambda_gae,
                entropy_coef,
            )

        # Save policy
        self.save_model()

        # Report to wandb
        self.report_to_wandb()
        wandb.finish()

    def report_to_wandb(self, b_plot_means: bool = True) -> None:
        """Reports the training results to wandb.

        Args:
            b_plot_means: Whether to plot the mean episode returns and lengths.
              Defaults to True.
        """
        envs_return_queue = np.array(self.envs_wrapper.return_queue).flatten()
        envs_length_queue = np.array(self.envs_wrapper.length_queue).flatten()

        # Episode returns (returns are the cumulative rewards)
        data = envs_return_queue.tolist()
        data = [[i, d] for i, d in enumerate(data)]
        table = wandb.Table(data=data, columns=["Episode", "Return"])
        wandb.log(
            {
                "Episode Returns": wandb.plot.line(
                    table, "Episode", "Return", title="Episode Returns"
                )
            }
        )

        # Episode lengths
        data = envs_length_queue.tolist()
        data = [[i, d] for i, d in enumerate(data)]
        table = wandb.Table(data=data, columns=["Episode", "Length"])
        wandb.log(
            {
                "Episode Lengths": wandb.plot.line(
                    table, "Episode", "Length", title="Episode Lengths"
                )
            }
        )

        # Success
        success_counts = Counter(self.episodes_success)
        data = [[k, v] for k, v in success_counts.items()]
        table = wandb.Table(data=data, columns=["Success", "Count"])
        wandb.log(
            {
                "Success": wandb.plot.bar(
                    table, "Success", "Count", title="Success"
                )
            }
        )

        if b_plot_means:
            # Plot to matplotlib (code updated from Gymnasium documentation)
            _, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 5))
            rolling_length = 100  # Number of episodes to average over

            # Mean episode returns
            axs[0][0].set_title("Episode Returns")
            episode_returns_moving_avg = (
                np.convolve(
                    envs_return_queue.flatten(),
                    np.ones(rolling_length),
                    mode="valid",
                )
                / rolling_length
            )
            axs[0][0].plot(
                np.arange(len(episode_returns_moving_avg)) / self.n_envs,
                episode_returns_moving_avg,
            )
            axs[0][0].set_xlabel("Number of episodes")
            axs[0][0].set_ylabel("Mean episode return")

            # Mean episode lengths
            axs[0][1].set_title("Episode Lengths")
            episode_lengths_moving_avg = (
                np.convolve(
                    envs_length_queue.flatten(),
                    np.ones(rolling_length),
                    mode="valid",
                )
                / rolling_length
            )
            axs[0][1].plot(
                np.arange(len(episode_lengths_moving_avg)) / self.n_envs,
                episode_lengths_moving_avg,
            )
            axs[0][1].set_xlabel("Number of episodes")
            axs[0][1].set_ylabel("Mean episode length")

            plt.tight_layout()
            wandb.log({"Training plots": wandb.Image(plt)})

        # Add data to wandb summary
        wandb.summary.update(
            {
                "Proportion of truncation": self.num_truncations
                / (self.n_envs * self.num_episodes * self.n_steps_per_episode),
                "Success rate": self.episodes_success.count(True)
                / len(self.episodes_success)
                if self.episodes_success
                else 0,
            }
        )
        wandb.finish()
