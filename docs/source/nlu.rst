Natural Language Understanding
------------------------------

The natural language understanding (NLU) component converts incoming user utterances into dialogue acts.
A dialogue act is a structured representation comprising an intent and parameters. A parameter is a triplet including a slot, operator, and value. Note that the user intents and slots, that are domain specific, are pre-defined and can easily be modified to fit a new domain.
The NLU process is divided into two steps: intent classification and slot filling.

Two types of NLU component are available:

- :py:class:`RuleBasedNLU <moviebot.nlu.rule_based_nlu.RuleBasedNLU>`: intents and parameters are extracted using pre-defined rules.
- :py:class:`NeuralNLU <moviebot.nlu.neural_nlu.NeuralNLU>`: intents and parameters are extracted using a JointBERT model with a CRF layer [1]_. Training data and scripts are released with the code.

User Intents
------------

:py:class:`UserIntents <moviebot.intents.user_intents>`

+--------------------------+----------------------------------------------+
| Intent                   | Description                                  |
+==========================+==============================================+
| Reveal                   | The user wants to reveal a preference.       |
+--------------------------+----------------------------------------------+
| Inquire                  | Once the agent has recommended an item,      |
|                          | the user can ask further details about it.   |
+--------------------------+----------------------------------------------+
| Remove preference        | The user wants to remove any previously      |
|                          | stated preference.                           |
+--------------------------+----------------------------------------------+
| Reject                   | The user either has already seen/consumed    |
|                          | the recommended item or does not like it.    |
+--------------------------+----------------------------------------------+
| Accept                   | The user accepts (likes) the recommendation. |
|                          | This will determine the success of the system|
|                          | as being able to find a satisfying           |
|                          | recommendation.                              |
+--------------------------+----------------------------------------------+
| Continue recommendation  | If the user likes a recommendation, they can |
|                          | either restart, quit, or continue the process|
|                          | to get a similar recommendation.             |
+--------------------------+----------------------------------------------+
| Restart                  | The user wants to restart the recommendation |
|                          | process.                                     |
+--------------------------+----------------------------------------------+
| Acknowledge              | Acknowledge the agent's question where       |
|                          | required.                                    |
+--------------------------+----------------------------------------------+
| Deny                     | Negate the agent's question where required.  |
+--------------------------+----------------------------------------------+
| Hi                       | When the user initiates the conversation,    |
|                          | they start with a formal hi/hello or reveal  |
|                          | preferences.                                 |
+--------------------------+----------------------------------------------+
| Bye                      | End the conversation by sending a bye message|
|                          | or an exit command.                          |
+--------------------------+----------------------------------------------+

Slots
-----

The slots are defined in the enumeration :py:class:`Slots <moviebot.nlu.annotation.slots.Slots>`. Note that some of these slots cannot be filled by the user, such as `imdb_link` and `cover_image`. 

**References**

.. [1] Chen, Q., Zhuo, Z., & Wang, W. (2019). BERT for Joint Intent Classification and Slot Filling. arXiv preprint arXiv:1902.10909.