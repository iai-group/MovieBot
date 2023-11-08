Reinforcement Learning
======================

This package contains all the resources to train a dialogue policy using reinforcement learning. It comprises:

* Gymnasium environments
* Training scripts

Gymnasium environments
----------------------

Two environment are provided:

* `DialogueEnvMovieBotNoNLU-v0`: during training the NLU component of the agent is not user. That is, the dialogue policy receives the structured representation of the user simulator's responses as input.
* `DialogueEnvMovieBot-v0`: during training the NLU component of the agent is used. That is, the dialogue policy receives the output of the NLU component as input.

Note that to use the environments you will need to import them from the :py:mod:`reinforcement_learning.environment` package, for example:

.. code-block:: python

    from reinforcement_learning.environment import DialogueEnvMovieBot

Training scripts
----------------

Currently, there are two reinforcement learning algorithms supported:

* Deep Q-Learning
* Advantage Actor-Critic

Each algorithm has its own trainer, which can be found in the :py:mod:`reinforcement_learning.training` package.

Before training a dialogue policy, you need to prepare a configuration file.
A default configuration for each supported algorithm is provided in the `reinforcement_learning/config` folder.

A dialogue policy is trained by executing the following command:

.. code-block:: bash

    python -m reinforcement_learning.train_dialogue_policy -c <training_configuration>

The training logs are stored in Weight and Biases. It implies that you have an account on Weight and Biases and your are logged in. More information can be found `here <https://docs.wandb.ai/quickstart>`_.

Training Configuration
^^^^^^^^^^^^^^^^^^^^^^

The training configuration is used to specify paths to participants configuration files, model's parameters, training hyperparameters, and other options related to training. Below is an empty configuration file with main options:

.. code-block:: yaml

    # Participants' configuration
    usersim_config: <path to user simulator configuration>
    agent_config: <path to IAI MovieBot configuration>

    # Model's parameters
    model:
    algorithm: <dqn OR a2c>
    policy_input_size: 
    hidden_size: 
    model_path: <path to saved model>

    # Training hyperparameters
    hyperparams:
    hyperparam_name: hyperparam_value
    ...

    use_intents: 
    turn_penalty: 
    no_nlu: 

    debug: False

**Participants' configuration**: The participants' configuration files are used to specify the parameters of the user simulator and the agent.

**Model's parameters**: The model's parameters are used to specify the parameters of the dialogue policy model. The `algorithm` parameter is used to specify the type of the algorithm used, which can be either `dqn` or `a2c`. The `policy_input_size` parameter is used to specify the size of the input of the policy network. The `hidden_size` parameter is used to specify the size of the hidden layers of the policy network. The `model_path` parameter is used to specify the path to the saved model.

**Hyperparameters**: This section is reserved for training hyperparameters such as learning_rate, discount factor, etc. The hyperparameters are algorithm-specific and can be loaded easily in a dictionary.

**use_intents**: Specifies whether the markovian state should include intents.

**turn_penalty**: Specifies the turn penalty value that is included in the reward computation. In this context, a turn includes one utterance from each participant. The turn penalty concerns the current turn, i.e., the turn during which the reward is computed.

**no_nlu**: Specifies whether the user simulator's responses are processed by the agent's NLU module or not. If not, the agent takes the structured representation of the user simulator's responses as input.

User Simulator
--------------

The user simulator is built on top of `UserSimCRS <https://github.com/iai-group/UserSimCRS/tree/main>`_.
It is an agenda-based user simulator adapted for reinforcement learning.
In our case, the user simulator needs to send its response directly to the agent instead of letting the dialogue connector handle it.

We note that its architecture is the same as the one used in the UserSimCRS.

Try dialogue policy
-------------------

A dialogue policy can be tested with a human user via the terminal. Instead of interacting with the user simulator, the dialogue policy will interact with the user.

Execute the following command to test a dialogue policy:

.. code-block:: bash

    python -m reinforcement_learning.run_dialogue_policy --agent_config <path to IAI MovieBot configuration> --artifact_path <W&B artifact name> --model_path <path to saved model in W&B>

