ACCESS_TOKEN = 'EAAF5ZA8L6hnUBAH9CjUB2YExM9WMvi3CitPQOzivVwnC3NEKZB7pxhxHeUrXmEDFMqTBEfJZCkV5MUGV3hyT2vppi3w80YBHzO5oMow7iOAfQxEpunp2w2EVSDn1Sq1e32ItNDdQMZAkzdjxMQSdzzKhcy6nsrj3dBIDUfalJt1XYcc7dppy'
VERIFY_TOKEN = 'bonobo'

button = 'https://graph.facebook.com/v2.6/me/messages?access_token='+ACCESS_TOKEN
persistent_menu = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+ACCESS_TOKEN
media = 'https://graph.facebook.com/v9.0/me/message_attachments?access_token='+ACCESS_TOKEN
message = 'https://graph.facebook.com/v9.0/me/messages?access_token='+ACCESS_TOKEN
get_started = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+ACCESS_TOKEN
images = 'https://graph.facebook.com/v9.0/me/message_attachments?access_token='+ACCESS_TOKEN

text = {
            'recipient': {},
            'message': {}
        }

template = {
  "recipient":{
  },
  "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"generic",
        "elements":[
           {
            "title":"Welcome!",
            "image_url":"https://m.media-amazon.com/images/M/MV5BODI4NDY2NDM5M15BMl5BanBnXkFtZTgwNzEwOTMxMDE@._V1_FMjpg_UX1000_.jpg",
            "subtitle":"At the end of his career, a clueless \
            fashion model is brainwashed to kill the Prime Minister of Malaysia. ",
            "default_action": {
              "type": "web_url",
              "url": "https://www.imdb.com/title/tt0196229/?ref_=hm_tpks_tt_2_pd_tp1_cp",
              "webview_height_ratio": "tall",
            },
            "buttons":[
              {
                "type":"web_url",
                "url":"https://www.nrk.no/",
                "title":"View Website"
              },{
                "type":"postback",
                "title":"Yes",
                "payload":"DEVELOPER_DEFINED_PAYLOAD"
              },
              {
                "type":"postback",
                "title":"No",
                "payload":"DEVELOPER_DEFINED_PAYLOAD"
              }
                 
            ]      
          }
        ]
      }
    }
  }
}

menu = {
    #"psid": recipient_id,

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
                    "url": "https:/wikipedia.com/",
                    "webview_height_ratio": "full"
                }
            ]
        }
    ]
}

def url_button(recipient_id, text, url, title):
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
                    "type": "web_url",
                    "url": url,
                    "title": title
                    }
                ]
            }
            }
        }
    }
    return button

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

image = {
    "recipient": {
    },
    "message":{
        "attachment":{
        "type":"image", 
        "payload":{
          "is_reusable": True,
          "url": "https://i.imgur.com/ceuUozR.jpeg"
        }
        }
    }
}