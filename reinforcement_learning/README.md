# Reinforcement Learning

This package contains all the resources to train a dialogue policy using reinforcement learning. It comprises:

  * Gymnasium environments
  * Training scripts

## Gymnasium environments

To use the environments, you first need to register them with Gymnasium, to do so you need to execute their attached script. For example, to register the `DialogueEnvMovieBot-v0` environment, you need to execute the following command:

```bash
python -m reinforcement_learning.environment.dialogue_env_moviebot
```

Note that to use the environments you will need to import them from the `reinforcement_learning.environment` package, for example:

```python
from reinforcement_learning.environment import DialogueEnvMovieBot
```
