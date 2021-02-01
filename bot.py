import requests, json


#Using FB graph API
FACENBOOK_GRAPH_URL = 'https://graph.facebook.com/v9.0/me/'



class Bot(object):
  def __init__(self,access_token, api_url=FACENBOOK_GRAPH_URL):
    self.access_token = access_token
    self.api_url = api_url

  def send_message(self, psid, message, messaging_type='RESPONSE'):
    headers = {
      'Content-Type': 'application/json'
    }
    data = {
      'messaging_type':messaging_type,
      'recipient':{'id':psid},
      'message':{'text':message}
    }

    params = {'access_token': self.access_token}
    self.api_url = self.api_url + 'messages'

    response = requests.post(self.api_url, headers = headers, params=params, data=json.dumps(data))


  def send_quickbuttons(self, psid, message, messaging_type='RESPONSE'):
    headers = {
      'Content-Type': 'application/json'
    }
    data = {
      'messaging_type':messaging_type,
      'recipient':{'id':psid},
      'message':{'text':message, 'quick_replies':[
        {
          'content_type':'text',
          'title':'Action', #Displayed on button
          'payload':'Action' #Sent back to bot
        },{
          'content_type':'text',
          'title':'Fantasy',
          'payload':'Fantasy'
        },{
          'content_type':'text',
          'title':'Sci-fi',
          'payload':'Sci-fi'
        }
      ]
                 }
    }

    params = {'access_token': self.access_token}
    self.api_url = self.api_url + 'messages'

    response = requests.post(self.api_url, headers = headers, params=params, data=json.dumps(data))

  def send_movieimg(self, psid, message, img, messaging_type='RESPONSE'):
      headers = {
        'Content-Type': 'application/json'
      }

      data = {
        'messaging_type':messaging_type,
        'recipient':{'id':psid},
        'message':{ 
            'attachment':{
            'type':'image',
            'payload':{
                'url':img
            }
        },
         'quick_replies':[
          {
            'content_type':'text',
            'title':'Id like more!', #Displayed on button
            'payload':'AM0I', #Sent back to bot
            'image_url':'https://www.pinclipart.com/picdir/middle/538-5389478_-mint-plain-green-pastel-circle-color-colour.png'
          },{
            'content_type':'text',
            'title':'Not Interested',
            'payload':'Not Interested'
          },
          {
            'content_type':'text',
            'title':'Stop',
            'payload':'Stop',
            'image_url':'https://lh3.googleusercontent.com/proxy/upsXiwUR9I01YLLfSgp8ZjRkb2ZY1sahIp8lERrxcnwn-M1YTGzNBa45kQd-aZBfCg0341jAE-mrHup2XgiZAKghyplv56k'
          }
        ]
                  }
      }

      params = {'access_token': self.access_token}
      self.api_url = self.api_url + 'messages'

      response = requests.post(self.api_url, headers = headers, params=params, data=json.dumps(data))

  def send_link(self, psid, message, url='', messaging_type='RESPONSE'):
      headers = {
        'Content-Type': 'application/json'
      }
      data = {
        'messaging_type':messaging_type,
        'recipient':{'id':psid},
        "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":message,
        "buttons":[
          {
            "type":"web_url",
            "url":"https://www.imdb.com/title/tt0468569/?ref_=adv_li_tt",
            "title":"To imbd",
            "webview_height_ratio": "full"
          }
        ]
      }
    }
  }
  }

      params = {'access_token': self.access_token}
      self.api_url = self.api_url + 'messages'

      response = requests.post(self.api_url, headers = headers, params=params, data=json.dumps(data))
