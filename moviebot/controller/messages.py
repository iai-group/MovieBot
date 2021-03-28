import requests

class Messages:

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.buttons = {}
        self.token = token

    def quickreply(self, text, title, payload):
        replies = []
        for i, title in enumerate(title):
            replies.append({
                "content_type":"text",
                "title": title,
                "payload":payload[i]
            })
        quick_reply = {
            "recipient": {
                "id": self.user_id
            },
            "messaging_type": "RESPONSE",
            "message":{
                "text": text,
                "quick_replies":replies
            }
            
        }
        return requests.post("https://graph.facebook.com/v10.0/me/messages?access_token="+self.token, json=quick_reply).json()

    def create_buttons(self, options):
        buttons = []
        for option in options:
            buttons.append(
                {"type": "postback", "title": option['title'], "payload": option['payload']}
            )
        #self.buttons = buttons
        return buttons

    def typing_on(self):
        typing = {
            "recipient":{"id": self.user_id},
            "sender_action": "typing_on"
        }
        return requests.post('https://graph.facebook.com/v2.6/me/messages?access_token='+self.token, json=typing).json()

    def mark_seen(self):
        mark_seen = {
            "recipient": {"id": self.user_id},
            "sender_action": "mark_seen"
            }
        return requests.post('https://graph.facebook.com/v2.6/me/messages?access_token='+self.token, json=mark_seen).json()
    
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
                    "title":title,
                    "image_url":image,
                    "subtitle":subtitle,
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
        return requests.post('https://graph.facebook.com/v9.0/me/messages?access_token='+self.token, json=template).json()

    def buttons_template(self, buttons, text):
        template = {
            "recipient":{ "id": self.user_id},
            "message":{
            "attachment":{
                "type":"template",
                "payload":{
                "template_type":"button",
                "text":text,
                "buttons":buttons
                }
            }
            }
        }
        return requests.post('https://graph.facebook.com/v2.6/me/messages?access_token='+self.token, json=template).json()
    
    
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
