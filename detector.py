import os

from flask import Flask, Response
from werkzeug.wrappers import Request

import request as r
from evolution import Evolution
from request_parser import BodyParser, QueryParser

class Detector(object):
    """
        Middleware for detecting hacks
    """

    def __init__(self, app: Flask):
        self.app = app
        self.evolution: Evolution = Evolution.load('499', './checkpoints')
        self.body_parser = BodyParser.load()
        self.query_parser = QueryParser.load()
        
        try:
            os.system('cls')
        except:
            os.system('clear')

    def __call__(self, environ, start_response):
        """
            Called by middleware. Actually does the detecting.
        """
        
        request = Request(environ)

        data = r.Request({
            "method": request.method,
            "content_length": request.content_length,
            "protocol": request.environ.get('SERVER_PROTOCOL'),
            "is_hack": None
        })

        output = self.evolution.predict(data)
        self.score = output[0] * 100

        prediction = output[0] < 0

        body_probability = self.body_parser.predict(request.get_data().decode('utf-8'))[0]
        query_probabiliy = self.query_parser.predict(request.query_string.decode('utf-8'))[0]

        body_probability = round(body_probability)
        query_probabiliy = round(query_probabiliy)
        
        if prediction or (bool(body_probability) or bool(query_probabiliy)):
            # Its a hack
            res = Response(u'Hack detected {0} % sure \nRequest {1}\nRaw Score: {2}'.format(self.score, data.to_dict(), output),
                        mimetype='text/plain', status=404)
            return res(environ, start_response)
        
        # Not a hack!
        res = Response(u'Not Hack {0} % sure \nRequest {1}\nRaw Score: {2}\n\nQuery'.format(self.score, data.to_dict(), output),
                        mimetype='text/plain', status=200)
        return res(environ, start_response)
        
        



