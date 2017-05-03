"""
Differential synchronization logic for server.
"""


from bottle import Bottle, route, run, get, static_file, request, abort

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

import diff_match_patch as dmp

def conveyor_belt(consumer):
    """ An entry point coroutine that adds socket requests to 
    the consumer() coroutine.
    """
    try:
        while True:
            wsock, url = (yield)
            message = wsock.receive()
            next_step = consumer()
            next(next_step)
            next_step.send((wsock, url, message)) # shadowing consumer()

    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        next_step.close()
    except StopIteration:
        return None

def consumer():

    # TODO: can identify incoming connection via request.environ dict:
    # environ['REMOTE_ADDR']
    # environ['REMOTE_PORT']
    # print("environ:", wsock.environ)

    try:
        while True:
            wsock, url, message = (yield)
            wsock.send('Your message was: %r' % message)
            wsock.send('Your addr is: %s' %(wsock.environ['REMOTE_ADDR']))
            wsock.send('Your port is: %s' %(wsock.environ['REMOTE_PORT']))
            wsock.send('Your doc name is: %s' %(url))
    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        return None
    except StopIteration:
        return None
