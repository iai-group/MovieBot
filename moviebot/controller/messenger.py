import requests

class Messenger:

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.buttons = {}
        self.token = token
        self.quick_reply_uri = "https://graph.facebook.com/v10.0/me/messages?access_token="+self.token
        self.url_button_uri = "https://graph.facebook.com/v2.6/me/messages?access_token="+self.token
        self.text_uri = 'https://graph.facebook.com/v9.0/me/messages?access_token='+self.token
        self.template_uri = 'https://graph.facebook.com/v9.0/me/messages?access_token='+self.token
        self.button_template_uri = 'https://graph.facebook.com/v2.6/me/messages?access_token='+self.token
        self.typing_on_uri = 'https://graph.facebook.com/v2.6/me/messages?access_token='+self.token
        self.mark_seen_uri = 'https://graph.facebook.com/v2.6/me/messages?access_token='+self.token

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
        return requests.post(self.quick_reply_uri, json=quick_reply).json()

    def create_buttons(self, options):
        buttons = []
        for option in options:
            if option['button_type'] == "postback":
                buttons.append(
                {"type": option['button_type'], "title": option['title'], "payload": option['payload']}
                )
            if option['button_type'] == "web_url":
                buttons.append(
                    {"type": option['button_type'], "title": option['title'], "url": option['url']}
                )
        return buttons

    def url_button(self, title, options):
        buttons = self.create_buttons(options)
        template = \
        {
            "recipient":{
                "id": self.user_id
            },
            "message":{
                "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text": title,
                    "buttons": buttons
                }
                }
            }
        }
        return requests.post(self.url_button_uri, json=template).json()

    def typing_on(self):
        typing = {
            "recipient":{"id": self.user_id},
            "sender_action": "typing_on"
        }
        return requests.post(self.typing_on_uri, json=typing).json()

    def mark_seen(self):
        mark_seen = {
            "recipient": {"id": self.user_id},
            "sender_action": "mark_seen"
            }
        return requests.post(self.mark_seen_uri, json=mark_seen).json()
    
    def text(self, message):
            text = {
                'recipient': {'id': self.user_id},
                'message': {'text': message}
            }
            return requests.post(self.text_uri, json=text).json()

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
        return requests.post(self.template_uri, json=template).json()

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
        return requests.post(self.button_template_uri, json=template).json()
    

