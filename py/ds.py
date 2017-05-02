"""
Differential synchronization logic for server.
"""


from bottle import Bottle, route, run, get, static_file, request, abort

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

import threading

import diff_match_patch as dmp

def convey(wsock, message, pathname=None):

    # TODO: can identify incoming connection via request.environ dict:
    # environ['REMOTE_ADDR']
    # environ['REMOTE_PORT']
    # print("environ:", wsock.environ)

    try:
        wsock.send('Your message was: %r' % message)
        wsock.send('Your addr is: %s' %(wsock.environ['REMOTE_ADDR']))
        wsock.send('Your port is: %s' %(wsock.environ['REMOTE_PORT']))
        wsock.send('Your doc name is: %s' %(pathname))
    except WebSocketError:
        wsock.close()
