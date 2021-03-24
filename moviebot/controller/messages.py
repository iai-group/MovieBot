import requests

class Messages:

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.buttons = {}
        self.token = token

    def send_quickreply(self, text):
        quick_reply = {
            "recipient": {
                "id": self.user_id
            },
            "messaging_type": "RESPONSE",
            "message":{
                "text": text,
                "quick_replies":[
                {
                    "content_type":"text",
                    "title": "Accept",
                    "payload":"Accept"
                },{
                    "content_type":"text",
                    "title":"Reject",
                    "payload":"Reject"
                }
                ]
            }
            
        }
        return requests.post("https://graph.facebook.com/v10.0/me/messages?access_token="+self.token, json=quick_reply).json()

    def persistent_menu(self):
        menu = {
            "get_started":{
                "payload": "start"
            },
            "persistent_menu": [
                {
                    "locale": "default",
                    "composer_input_disabled": False,
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "Talk to an agent",
                            "payload": "CARE_HELP"
                        },
                        {
                            "type": "postback",
                            "title": "Outfit suggestions",
                            "payload": "CURATION"
                        }
                    ]
                }
            ]
        }
        return requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+self.token, json=menu).json()

    def text(self, message):
            text = {
                'recipient': {'id': self.user_id},
                'message': {'text': message}
            }
            return requests.post('https://graph.facebook.com/v9.0/me/messages?access_token='+self.token, json=text).json()

    def template(self, buttons, image, url, subtitle, title):
        template = {
            "recipient":{ "id": self.user_id},
            "message":{
            "attachment":{
                "type":"template",
                "payload":{
                "template_type":"generic",
                "elements":[
                    {
                    "title":title + " " + str(rating) + " " + str(duration) + " min",
                    "image_url":poster,
                    "subtitle":plot,
                    "default_action": {
                        "type": "web_url",
                        "url": url,
                        "webview_height_ratio": "full",
                    },
                    "buttons": buttons
                    }
                ]
                }
            }
            }
        }
        return template

    def buttons_template(self, buttons):
        template = {
            "recipient":{ "id": self.user_id},
            "message":{
            "attachment":{
                "type":"template",
                "payload":{
                "template_type":"button",
                "text":self.agent_response[user_id],
                "buttons":buttons
                }
            }
            }
        }
        return template

    def send_buttons(self, template):
        return requests.post('https://graph.facebook.com/v2.6/me/messages?access_token='+ACCESS_TOKEN, json=template).json()