"""Records the dialogue details of the conversation in it's raw form."""


class DialogueRecorder:
    def __init__(self, path: str, nlp: bool) -> None:
        """Initializes the recorder.

        If required, it also saves the dialogue acts.

        Args:
            path: Path to the save file.
            nlp: If true, the Dialogue Acts will also be saved.
        """
        self.path = path
        self.nlp = nlp
        # TODO: Check if file or folder exists/create file or change name
        # TODO: create a file with unique ID here

    def record(self) -> None:
        """Records the current dialogue utterance."""
        # TODO: record the data

    def save(self) -> None:
        """Saves all the dialogues in the conversation to a file."""
        # TODO: save the file
