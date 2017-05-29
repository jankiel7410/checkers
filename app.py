from os import path
import random
import string

from game import Game


import cherrypy
GAMES = {}


class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        if 'id' not in cherrypy.session:
            session_id = ''.join(random.sample(string.hexdigits, 16))
            cherrypy.session['id'] = session_id
            GAMES[session_id] = Game()
        return open('index.html')

    @cherrypy.expose
    def move(self, move):
        session_id = cherrypy.session['id']
        game = GAMES[session_id]
        game.move(move)
 
    @cherrypy.expose
    def end_turn(self):
        session_id = cherrypy.session['id']
        game = GAMES[session_id]
        

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/html')],
        },
        '/*': {
            'tools.response_headers.headers': [('Content-Type', 'text/json')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': path.abspath('.'),
        }
    }
    cherrypy.quickstart(HelloWorld(), '/', conf)
