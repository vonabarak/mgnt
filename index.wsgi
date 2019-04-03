
from mgnt.router import start

def application(environ, start_response):
    return start(environ, start_response)
