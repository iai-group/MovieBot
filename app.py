from flask import Flask, request
import json
from bot import Bot
import random

PAGE_ACCESS_TOKEN='EAA3t92dlcAsBAD7TTHtDRtNQEQ3tWXUGh3j1zyPQwdz4W5e1Vn2Rp8ZBmZBzm1jaQKPAs9dA6aLq1KfJ8FAdWvOCZAJQjxdyB4aUuXScr1qIX9hOyykzBK2TqV80znDcrW1QxHPScAmgMZBeIB2ZBG4ZByXcKZA5Kdsa16Ol0uF5AZDZD'
GREETINGS = ['hey', 'sup','hi', 'hello']
RPS = ['rock', 'paper', 'scissors']


app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def receive_message():
    #GET
    if request.method == 'GET':
        #Token security check
        VERIFY_TOKEN = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if VERIFY_TOKEN == 'RPSToken':
            return str(challenge)
        return '400'


    #POST, sent to bot
    else:
        data = json.loads(request.data)
        messaging_events = data['entry'][0]['messaging']
        bot = Bot(PAGE_ACCESS_TOKEN)

        # Can be multiple messaging events, loops through all
        for msg in messaging_events:
            uid = msg['sender']['id']
            txtinput = msg['message'].get('text')
            responseMsg = 'PLACEHOLDER MSG'

            if txtinput == 'challenge':
                choice = RPS[random.randint(0,2)]
                responseMsg = choice
                bot.send_quickbuttons(uid,responseMsg)

            #Anything Else
            else:
                #Greeting Check
                words = txtinput.split()
                for word in words:
                    if word in GREETINGS:
                        responseMsg = 'Hello! Testing specific word'
                # TEST PRINTS
                #print(f'UID: {uid} - {txtinput}')
                bot.send_message(uid, responseMsg)

        return  '200'


if __name__ == '__main__':
    app.run(debug=True)
