ACCESS_TOKEN = 'EAAF5ZA8L6hnUBAH9CjUB2YExM9WMvi3CitPQOzivVwnC3NEKZB7pxhxHeUrXmEDFMqTBEfJZCkV5MUGV3hyT2vppi3w80YBHzO5oMow7iOAfQxEpunp2w2EVSDn1Sq1e32ItNDdQMZAkzdjxMQSdzzKhcy6nsrj3dBIDUfalJt1XYcc7dppy'
VERIFY_TOKEN = 'bonobo'

button = 'https://graph.facebook.com/v2.6/me/messages?access_token='+ACCESS_TOKEN
persistent_menu = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+ACCESS_TOKEN
media = 'https://graph.facebook.com/v9.0/me/message_attachments?access_token='+ACCESS_TOKEN
message = 'https://graph.facebook.com/v9.0/me/messages?access_token='+ACCESS_TOKEN
get_started = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+ACCESS_TOKEN
images = 'https://graph.facebook.com/v9.0/me/message_attachments?access_token='+ACCESS_TOKEN
quickreply = 'https://graph.facebook.com/v9.0/me/messages?access_token='+ACCESS_TOKEN
text = {
            'recipient': {},
            'message': {}
        }

def create_text(recipient_id, message):
  text = {
      'recipient': {'id': recipient_id},
      'message': {'message': message}
  }
  return text

def create_template(recipient_id, buttons, poster, url, plot, title, rating, duration):
  template = {
    "recipient":{
      "id": recipient_id
    },
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
                "webview_height_ratio": "tall",
              },
              "buttons": buttons
            }
          ]
        }
      }
    }
  }
  return template

menu = {
    "psid": "",

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
                },
                {
                    "type": "web_url",
                    "title": "Shop now",
                    "url": "https://wikipedia.com/",
                    "webview_height_ratio": "full"
                }
            ]
        }
    ]
}

def create_reply(title, payload):
  return {'content_type': 'text', 'title': title, 'payload': payload, 'image_url': ""}

def qreply(psid):
      quickreply= {
      'messaging_type':'RESPONSE',
        'recipient':{'id':psid},
        'message':{
          'text': "More information",
          'quick_replies':[]
        }
        
      }
      return quickreply
    


# def url_button(recipient_id, text, url, title):
#     button = {
#         "recipient":{
#             "id": recipient_id
#         },
#         "message":{
#             "attachment":{
#                 "type":"template",
#                 "payload":{
#                     "template_type":"button",
#                     "text": text,
#                     "buttons":[
#                     {
#                     "type": "web_url",
#                     "url": url,
#                     "title": title
#                     }
#                 ]
#             }
#             }
#         }
#     }
#     return button

def postback_button(recipient_id, text, payload, title):
    button = {
        "recipient":{
            "id": recipient_id
        },
        "message":{
            "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text": text,
                "buttons":[
                {
                    "type": "postback",
                    "title": title,
                    "payload": payload
                }
                ]
            }
            }
        }
      }
    return button



def buttons_template(recipient_id, buttons):
  buttons = {
    "recipient":{ "id": recipient_id},
    "message":{"attachment":{"type":"template","payload":{
          "template_type":"button",
          "text":"What do you want to do next?",
          "buttons":buttons
        }
      }
    }
  }
  return buttons

def template_button(btype, title, payload):
  button = {"type": btype, "title": title, "payload": payload}
  return button

# image = {
#     "recipient": {
#     },
#     "message":{
#         "attachment":{
#           "type":"image", 
#           "payload":{
#             "is_reusable": True,
#             "url": "https://i.imgur.com/ceuUozR.jpeg"
#           }
#         }
#     }
# }