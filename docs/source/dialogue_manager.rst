Dialogue Manager
================

The :py:class:`DialogueManager <moviebot.dialogue_manager.dialogue_manager>` tracks the dialogue state and decides what action the system should take.
It comprises a dialogue state tracker and a dialogue policy.


Dialogue State Tracker
----------------------

This component is responsible for keeping track of the dialogue state and dialogue context based on the dialogue acts of the agent and the user.
In the current implementation, :py:class:`DialogueStateTracker <moviebot.dialogue_manager.dialogue_state_tracker>` is rule-based.

Dialogue Policy
---------------

This component decides what is the next action of the system based on the current dialogue state, i.e., it generates the next dialogue act of the system.
It defines the flow of the conversation, i.e., what steps an agent must take at every stage. 
MovieBot supports two types of dialogue policies: rule-based and neural-based.

Rule-based Dialogue Policy
^^^^^^^^^^^^^^^^^^^^^^^^^^

Based on a set of pre-defined rules and the current dialogue state, this policy decides the next action of the system.
The rule-based dialogue policy is implemented in the :py:class:`RuleBasedDialoguePolicy <moviebot.dialogue_manager.rb_dialogue_policy>` class.

Neural-based Dialogue Policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this type of policy, the dialogue state is represented as a vector, referred to as Markovian state. 
The Markovian state is either a concatenation of boolean flags present in the dialogue state or a concatenation of these flags and one-hot encoded vectors of the user's and system's last action.
It serves as input to a neural network that outputs the next probable action of the system.

Two neural dialogue policies are supported:

- :py:class:`DQNDialoguePolicy <moviebot.dialogue_manager.dialogue_policy.dqn_dialogue_policy>`: multi-layer perceptron trained to learn optimal action-value functions that maximize the expected cumulative reward.
- :py:class:`A2CDialoguePolicy <moviebot.dialogue_manager.dialogue_policy.a2c_dialogue_policy>`: actor and critic models trained simultaneously to learn an optimal policy and value function respectively.

The neural dialogue policies can be trained using reinforcement learning as described :doc:`here <reinforcement_learning>`.
