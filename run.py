#!/usr/bin/env python3

from wsgiref.simple_server import make_server
from mgnt.router import start


def application(environ, start_response):
    return start(environ, start_response)


port = 8000
httpd = make_server('', port, application)
httpd.serve_forever()
