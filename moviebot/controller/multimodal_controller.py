from moviebot.controller.controller import Controller

class ControllerMultiModal(Controller):

    def __init__(self):
        """Initializes some basic structs for the Controller.
        """
        self.agent = {}
        self.configuration = None
        self.user_options = {}
        self.response = {}
        self.record_data_agent = {}
        self.record_data = {}
        self.token = ''

