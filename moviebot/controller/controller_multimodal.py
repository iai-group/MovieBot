from moviebot.controller.controller import Controller
from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = 'bonobo'
CONTROLLER = ControllerMessenger()

def run():
    app.run(host='0.0.0.0', port=environ.get("PORT", 5000))

@app.route('/', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)

    else:   
        # if True:
        #     return ""
        output = request.get_json()
        #print(output)
        CONTROLLER.input(output)
        return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

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

