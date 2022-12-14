"""Record all the details of each dialogue in the conversation in it's raw form.
If required, it also saves the dialogue acts.
"""


class DialogueRecorder:
    """Record all the details of each dialogue in the conversation in it's raw form.
    If required, it also saves the dialogue acts."""

    def __init__(self, path, nlp):
        """Initializes the Recorder

        Args:
            path: Path where the file must be saved
            nlp: If the Dialogue Acts must also be saved

        """
        self.path = path
        self.nlp = nlp
        # TODO: Check if file or folder exists/create file or change name
        # TODO: create a file with unique ID here

    def record(self):
        """Records the current dialogue utterance"""
        # TODO: record the data

    def save(self):
        """Saves all the dialogues in the conversation to a file"""
        # TODO: save the file
