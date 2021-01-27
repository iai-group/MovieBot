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
          'title':'Rock',
          'payload':'Rock'
        },{
          'content_type':'text',
          'title':'Paper',
          'payload':'Paper'
        },{
          'content_type':'text',
          'title':'Scissors',
          'payload':'Scissors'
        }
      ]
                 }
    }

    params = {'access_token': self.access_token}
    self.api_url = self.api_url + 'messages'

    response = requests.post(self.api_url, headers = headers, params=params, data=json.dumps(data))

