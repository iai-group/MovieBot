# Reinforcement Learning

This package contains all the resources to train a dialogue policy using reinforcement learning. It comprises:

  * Gymnasium environments
  * Training scripts

## Gymnasium environments

To use the environments, you first need to register them with Gymnasium, to do so you need to execute their attached script.
For example, to register the `DialogueEnvMovieBot-v0` environment, you need to execute the following command:

```bash
python -m reinforcement_learning.environment.dialogue_env_moviebot
```

Note that to use the environments you will need to import them from the `reinforcement_learning.environment` package, for example:

```python
from reinforcement_learning.environment import DialogueEnvMovieBot
```

## Training scripts

Currently, there are two reinforcement learning algorithms supported: deep q-learning and advantage actor-critic.
Each algorithm has its own training script, which can be found in the `reinforcement_learning.training` package:

  * `train_dqn.py`: Deep Q-Learning
  * `train_a2c.py`: Advantage Actor-Critic

The training logs are stored in Weight and Biases.

### Deep Q-Learning

To train a dialogue policy using deep q-learning, you need to execute the `train_dqn.py` script.

```bash
```

### Advantage Actor-Critic

To train a dialogue policy using advantage actor-critic, you need to execute the `train_a2c.py` script.

```bash
```

Note that this algorithm does not support GPU training.

## Try dialogue policy

To try a dialogue policy, you need to execute the `run_policy.py` script.

```bash
```

This script allows to run a dialogue policy in a Gymnasium environment with a human user.
The user interact with the dialogue policy via the terminal.
