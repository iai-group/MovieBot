import endpoints
import requests

def sender_action(recipient):
    typing = {
        'recipient':{
            'id': recipient
        },
        'sender_action':"mark_seen"
        }
    return requests.post(endpoints.button, json=typing).json()