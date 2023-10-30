"""Trainer for DQN."""

import random
from collections import deque, namedtuple
from itertools import count
from typing import List

import confuse
import torch
from matplotlib import pyplot as plt

import wandb
from moviebot.dialogue_manager.dialogue_policy.dqn_dialogue_policy import (
    DQNDialoguePolicy,
)
from reinforcement_learning.training.trainer import Trainer

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

Transition = namedtuple(
    "Transition", ("state", "action", "next_state", "reward")
)


class ReplayMemory(object):
    def __init__(self, capacity: int) -> None:
        """Create Replay memory.

        Args:
            capacity: The max number of experiences that the memory can store.
        """
        self.memory = deque([], maxlen=capacity)

    def push(self, *args) -> None:
        """Saves a transition."""
        self.memory.append(Transition(*args))

    def sample(self, batch_size: int) -> List[Transition]:
        """Sample a batch of experiences."""
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        """Returns the length of the memory."""
        return len(self.memory)


class TrainerDQN(Trainer):
    def __init__(self, config: confuse.Configuration) -> None:
        """Initializes the trainer.

        Args:
            config: Training configuration.
        """
        super().__init__(config)

    def initialize_policy(self) -> None:
        """Initializes the policy and target networks."""
        policy_input_size = self.config["model"]["policy_input_size"].get()
        hidden_size = self.config["model"]["hidden_size"].get()
        output_size = len(self.agent_possible_actions)

        self.policy = DQNDialoguePolicy(
            input_size=policy_input_size,
            hidden_size=hidden_size,
            output_size=output_size,
            possible_actions=self.agent_possible_actions,
        ).to(DEVICE)

        self.target = DQNDialoguePolicy(
            input_size=policy_input_size,
            hidden_size=hidden_size,
            output_size=output_size,
            possible_actions=self.agent_possible_actions,
        ).to(DEVICE)
        self.target.load_state_dict(self.policy.state_dict())

        wandb.watch(self.policy)
        wandb.watch(self.target)

    def get_action(
        self,
        state: torch.Tensor,
    ) -> torch.Tensor:
        """Selects either an action based on the current state or a random one.

        Args:
            state: The current state.

        Returns:
            The id of selected action.
        """
        sample = random.random()
        eps_start = self.hyperparameters.get("eps_start")
        eps_decay = self.hyperparameters.get("eps_decay")
        eps_end = self.hyperparameters.get("eps_end")

        eps_threshold = eps_end + (eps_start - eps_end) * torch.exp(
            torch.tensor(-1.0 * self.steps_done / eps_decay)
        )
        if sample > eps_threshold:
            with torch.no_grad():
                return self.policy.select_action(state)[0]
        else:
            return torch.tensor(
                [[self.env.action_space.sample()]],
                device=DEVICE,
                dtype=torch.long,
            )

    def optimize_model(
        self,
        batch_size: int,
        gamma: float,
    ) -> None:
        """Performs a single optimization step on the policy network.

        Args:
            batch_size: The batch size to use for training.
            gamma: The discount factor to use for training.
        """
        if len(self.memory) < batch_size:
            return

        transitions = self.memory.sample(batch_size)
        batch = Transition(*zip(*transitions))

        non_final_mask = torch.tensor(
            tuple(map(lambda s: s is not None, batch.next_state)),
            device=DEVICE,
            dtype=torch.bool,
        )
        non_final_next_states = torch.cat(
            [s for s in batch.next_state if s is not None]
        )

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = self.policy(state_batch).gather(1, action_batch)

        next_state_values = torch.zeros(batch_size, device=DEVICE)
        with torch.no_grad():
            next_state_values[non_final_mask] = (
                self.target(non_final_next_states).max(1)[0].detach()
            )

        expected_state_action_values = (
            next_state_values * gamma
        ) + reward_batch

        criterion = torch.nn.SmoothL1Loss()
        loss = criterion(
            state_action_values, expected_state_action_values.unsqueeze(1)
        )

        wandb.log({"loss": loss})

        self.optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 100)
        self.optimizer.step()

    def train_episode(
        self,
        episode: int,
        batch_size: int,
        policy_input_size: int,
        gamma: float,
        tau: float,
    ) -> None:
        """Trains the policy for one episode.

        Args:
            episode: Episode number.
            batch_size: Batch size to use for training.
            policy_input_size: Size of the input vector.
            gamma: Discount factor.
            tau: Soft update factor.
        """
        # Initialize the environment and get initial state
        state, _ = self.env.reset()
        state = torch.tensor([state], device=DEVICE, dtype=torch.float)

        for timestep in count():
            if state.shape[1] != policy_input_size:
                raise ValueError(
                    f"State shape {state.shape} ({state}) doesn't match policy "
                    f"input size {policy_input_size} ({episode}, {timestep})"
                )
            # Select and perform an action
            action = self.get_action(state)
            self.steps_done += 1
            next_state, reward, terminated, truncated, info = self.env.step(
                action.item()
            )
            done = terminated or truncated

            if terminated:
                next_state = None
            elif truncated:
                self.num_truncations += 1
                next_state = None
            else:
                next_state = torch.tensor(
                    [next_state], device=DEVICE, dtype=torch.float
                )

            self.episodes_rewards.append(reward)
            reward = torch.tensor([reward], device=DEVICE)

            # Store the transition in memory
            self.memory.push(state, action, next_state, reward)

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the target network)
            self.optimize_model(batch_size, gamma)

            # Soft update of the target network
            target_net_state_dict = self.target.state_dict()
            policy_net_state_dict = self.policy.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = (
                    tau * policy_net_state_dict[key]
                    + (1 - tau) * target_net_state_dict[key]
                )
            self.target.load_state_dict(target_net_state_dict)

            if done:
                self.episodes_durations.append(timestep + 1)
                self.episodes_success.append(info["success"])
                wandb.log(
                    {
                        "episode_duration": timestep + 1,
                        "episode_success": int(info["success"]),
                        "episode_reward": info["reward"],
                    }
                )
                break

    def train_policy(self) -> None:
        """Trains the policy."""
        # Create environment
        self.env = self.create_environment(b_vectorized=False)

        # Get training parameters
        self.hyperparameters = self.config["hyperparams"].get()
        batch_size = self.hyperparameters.get("batch_size")
        policy_input_size = self.config["model"]["policy_input_size"].get()
        gamma = self.hyperparameters.get("gamma")
        tau = self.hyperparameters.get("tau")

        # Initialize optimizer
        self.optimizer = torch.optim.AdamW(
            self.policy.parameters(),
            lr=self.hyperparameters["learning_rate"],
            amsgrad=True,
        )

        # Initialize replay memory
        self.memory = ReplayMemory(10000)

        self.steps_done = 0
        self.episodes_durations = []
        self.episodes_success = []
        self.episodes_rewards = []
        self.num_truncations = 0

        num_episodes = self.hyperparameters["n_episodes"]
        for episode in range(num_episodes):
            self.train_episode(
                episode, batch_size, policy_input_size, gamma, tau
            )

        # Save policy
        self.save_model()

        # Report to wandb
        self.report_to_wandb(num_episodes)
        wandb.finish()

    def report_to_wandb(self, num_episodes: int) -> None:
        """Adds training plots and data to wandb summary.

        Args:
            num_episodes: Number of episodes.
        """
        _, axs = plt.subplots(2, 1, figsize=(12, 15))
        # Plot average episode durations
        # Average over 100 episodes
        rolling_length = 100
        avg_durations = (
            torch.tensor(self.episodes_durations, dtype=torch.float)
            .unfold(0, rolling_length, 1)
            .mean(1)
            .view(-1)
        )
        avg_durations = torch.cat(
            (torch.zeros(rolling_length - 1), avg_durations)
        )
        axs[0].plot(avg_durations.numpy())
        axs[0].set_title("Average episode durations")
        axs[0].set_xlabel("Episode")
        axs[0].set_ylabel("Duration")

        # Plot average episode rewards
        # Average over 100 episodes
        avg_rewards = (
            torch.tensor(self.episodes_rewards, dtype=torch.float)
            .unfold(0, rolling_length, 1)
            .mean(1)
            .view(-1)
        )
        avg_rewards = torch.cat((torch.zeros(rolling_length - 1), avg_rewards))
        axs[1].plot(avg_rewards.numpy())
        axs[1].set_title("Average episode rewards")
        axs[1].set_xlabel("Episode")
        axs[1].set_ylabel("Reward")

        plt.tight_layout()
        wandb.log({"Training plots": wandb.Image(plt)})

        # Add data to wandb summary
        wandb.summary.update(
            {
                "Proportion of truncation": self.num_truncations / num_episodes,
                "Success rate": self.episodes_success.count(True)
                / len(self.episodes_success)
                if self.episodes_success
                else 0,
            }
        )
