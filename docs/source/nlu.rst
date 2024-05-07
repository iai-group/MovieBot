Natural Language Understanding
------------------------------

The natural language understanding (NLU) component converts incoming user utterances into dialogue acts.
A dialogue act is a structured representation comprising an intent and parameters. A parameter is a triplet including a slot, an operator, and a value. Note that the user intents and slots, that are domain specific, are pre-defined and can easily be modified to fit a new domain.
The NLU process is divided into two steps: intent classification and slot filling.

Two types of NLU component are available:

- :py:class:`RuleBasedNLU <moviebot.nlu.rule_based_nlu.RuleBasedNLU>`
- :py:class:`NeuralNLU <moviebot.nlu.neural_nlu.NeuralNLU>`

Rule-Based NLU
--------------

The rule-based NLU module utilizes a combination of keyword extraction and heuristics to determine the user's intent and extract slot-value pairs from their utterances. This approach relies on predefined rules and patterns to interpret user input.

Neural NLU with JointBERT
-------------------------

The Neural NLU module employs a JointBERT model with a CRF layer [1]_ to extract both the intent of the user's utterance and the corresponding slot-value pairs.

Training the JointBERT Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To train the JointBERT model, the provided training script (`moviebot/nlu/annotation/joint_bert/joint_bert_train.py`) can be utilized. This script downloads a pre-trained BERT model (`bert-base-uncased`) and fine-tunes it on a dataset annotated with intents and slot-value pairs. Below is an overview of the training process:

1. **Data Preparation**: Ensure the dataset is properly formatted with annotations for intents and slot-value pairs. The data path should be specified using the `--data_path` argument in the training script.

Example dataset format:

.. code-block:: yaml

    REVEAL:
    - text: "[I absolutely adore](modifier) movies focusing on [martial arts](keywords)."
    - text: "Films about [space exploration](keywords) [fascinate me](modifier)."
    - text: "[I can't stand](modifier) movies that emphasize on [corporate politics](keywords)."
    - text: "[Space adventures](keywords) [always intrigue me](modifier)."

2. **Model Initialization**: The model is initialized with the number of intent labels and slot labels based on the dataset. Additionally, hyperparameters such as learning rate, weight decay, and maximum epochs may be configured.

3. **Training**: The training script supports logging with `Wandb <https://wandb.ai/site>` for easy monitoring of training progress.

4. **Model Saving**: After training, the trained model weights are saved to the specified output path (`--model_output_path`). Additionally, metadata including intent and slot names is saved in a JSON file for reference.

6. **Usage**: Once trained, the JointBERT model can be integrated into the conversational system for natural language understanding tasks, by specifying the model path.

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

The slots are defined in the enumeration :py:class:`Slots <moviebot.nlu.annotation.slots.Slots>`. Note that some of these slots cannot be filled upon the reception of a user utterance, such as `imdb_link` and `cover_image`. 

**References**

.. [1] Chen, Q., Zhuo, Z., & Wang, W. (2019). BERT for Joint Intent Classification and Slot Filling. arXiv preprint arXiv:1902.10909.