from flask import Flask, request
import json
from bot import Bot
import random

PAGE_ACCESS_TOKEN='EAA3t92dlcAsBAD7TTHtDRtNQEQ3tWXUGh3j1zyPQwdz4W5e1Vn2Rp8ZBmZBzm1jaQKPAs9dA6aLq1KfJ8FAdWvOCZAJQjxdyB4aUuXScr1qIX9hOyykzBK2TqV80znDcrW1QxHPScAmgMZBeIB2ZBG4ZByXcKZA5Kdsa16Ol0uF5AZDZD'
GREETINGS = ['hey', 'sup','hi', 'hello']
MOVIE_PROMTS = ['Which would you like?', 'Pick a movie!', 'Have a gander!']
ACTION_MOVIES = ['The Dark Knight', 'The Lord of the Rings: The Return of the King', 'Avengers: Endgame']
IMDB_LINKS = {'The Dark Knight':'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_UX182_CR0,0,182,268_AL_.jpg',
            'The Lord of the Rings: The Return of the King':'https://m.media-amazon.com/images/M/MV5BNzA5ZDNlZWMtM2NhNS00NDJjLTk4NDItYTRmY2EwMWZlMTY3XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UX182_CR0,0,182,268_AL_.jpg',
            'Avengers: Endgame':'https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_UX182_CR0,0,182,268_AL_.jpg'
            }
IMDB_INFO = { #Fetch from imdb, check legality on webscraping
    'The Dark Knight': 'Title: a, Runtime: y, Rating: z\nSummary: x'
}
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


    #POST, sent to bot, for now only reads msg sent from user, doesnt keep track of conversation i.e. can type "Action" to skip the "movie" prompt 
    else:
        data = json.loads(request.data)
        messaging_events = data['entry'][0]['messaging']
        bot = Bot(PAGE_ACCESS_TOKEN)

        # Can be multiple messaging events, loops through all
        for msg in messaging_events:

            uid = msg['sender']['id']
            print(f'MESSAGE CHECK NO BOT: {msg}')
            txtinput = msg['message'].get('text')
            responseMsg = 'PLACEHOLDER MSG'
            output = request.get_json()
            print(output)
            print('--------------------------')
            
            #How the bot will react
             
            if txtinput == 'movie' or txtinput == 'Not Interested':
                choice = MOVIE_PROMTS[random.randint(0,2)]
                responseMsg = choice
                bot.send_quickbuttons(uid,responseMsg)
            elif txtinput == 'Action':
                movie = ACTION_MOVIES[0]
                responseMsg = movie
                img = IMDB_LINKS[movie]
                bot.send_movieimg(uid, responseMsg, img)
            elif txtinput == 'Fantasy':
                movie = ACTION_MOVIES[1]
                responseMsg = movie
                img = IMDB_LINKS[movie]
                bot.send_movieimg(uid, responseMsg, img)
            elif txtinput == 'Sci-fi':
                movie = ACTION_MOVIES[2]
                responseMsg = movie
                img = IMDB_LINKS[movie]
                bot.send_movieimg(uid, responseMsg, img)
                
                
            elif txtinput == 'Id like more!':
                rfrom flask import Flask, request
import json
from bot import Bot
import random

PAGE_ACCESS_TOKEN='EAA3t92dlcAsBAD7TTHtDRtNQEQ3tWXUGh3j1zyPQwdz4W5e1Vn2Rp8ZBmZBzm1jaQKPAs9dA6aLq1KfJ8FAdWvOCZAJQjxdyB4aUuXScr1qIX9hOyykzBK2TqV80znDcrW1QxHPScAmgMZBeIB2ZBG4ZByXcKZA5Kdsa16Ol0uF5AZDZD'
GREETINGS = ['hey', 'sup','hi', 'hello']
MOVIE_PROMTS = ['Which would you like?', 'Pick a movie!', 'Have a gander!']
ACTION_MOVIES = ['The Dark Knight', 'The Lord of the Rings: The Return of the King', 'Avengers: Endgame']
IMDB_LINKS = {'The Dark Knight':'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_UX182_CR0,0,182,268_AL_.jpg',
            'The Lord of the Rings: The Return of the King':'https://m.media-amazon.com/images/M/MV5BNzA5ZDNlZWMtM2NhNS00NDJjLTk4NDItYTRmY2EwMWZlMTY3XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UX182_CR0,0,182,268_AL_.jpg',
            'Avengers: Endgame':'https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_UX182_CR0,0,182,268_AL_.jpg'
            }
IMDB_INFO = { #Fetch from imdb, check legality on webscraping
    'The Dark Knight': 'Title: a, Runtime: y, Rating: z\nSummary: x'
}
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


    #POST, sent to bot, for now only reads msg sent from user, doesnt keep track of conversation i.e. can type "Action" to skip the "movie" prompt 
    else:
        data = json.loads(request.data)
        messaging_events = data['entry'][0]['messaging']
        bot = Bot(PAGE_ACCESS_TOKEN)

        # Can be multiple messaging events, loops through all
        for msg in messaging_events:

            uid = msg['sender']['id']
            
            txtinput = msg['message'].get('text')
            responseMsg = 'PLACEHOLDER MSG'
            output = request.get_json()
            
            #How the bot will react
             
            if txtinput == 'movie' or txtinput == 'Not Interested':
                choice = MOVIE_PROMTS[random.randint(0,2)]
                responseMsg = choice
                bot.send_quickbuttons(uid,responseMsg)
            elif txtinput == 'Action':
                movie = ACTION_MOVIES[0]
                responseMsg = movie
                img = IMDB_LINKS[movie]
                bot.send_movieimg(uid, responseMsg, img)
            elif txtinput == 'Fantasy':
                movie = ACTION_MOVIES[1]
                responseMsg = movie
                img = IMDB_LINKS[movie]
                bot.send_movieimg(uid, responseMsg, img)
            elif txtinput == 'Sci-fi':
                movie = ACTION_MOVIES[2]
                responseMsg = movie
                img = IMDB_LINKS[movie]
                bot.send_movieimg(uid, responseMsg, img)
                
                
            elif txtinput == 'Id like more!':
                responseMsg = IMDB_INFO['The Dark Knight']
                bot.send_link(uid,responseMsg)                
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
esponseMsg = IMDB_INFO['The Dark Knight']
                bot.send_link(uid,responseMsg)                
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
