"""
run with
    python3 server.py -e <ENV>
"""


from bottle import Bottle, route, run, get, static_file, request, abort, redirect

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

import ds

import threading
import argparse
import conf


# # @route('/w/<url:re:.+>')
# @route('/')
# def index():
#     return static_file('index.html', root="../")

@route('/w/<url:re:.+>')
def doc(url):
    # print(request.url)
    # redirect('/')
    return static_file('index.html', root="../")

@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="../static/css")

@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="../static/js")

# @get("/w/<url:re:.+>")
@get("/websocket/<url:re:.+>")
def socks(url=None):
    wsock = request.environ.get('wsgi.websocket')

    if not wsock:
        abort(400, 'Expected websocket request...')
    else:
        while True:
            try:
                message = wsock.receive()
                porter = threading.Thread(target=ds.convey,
                                        args=(wsock,message,url))
                porter.start()
            except WebSocketError:
                break

if __name__ == "__main__":
    """Start a passive socket. Parse CLI arguments for environment."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", type=str, default='TESTING', help="one of ['TESTING', 'PRODUCTION']")
    args = parser.parse_args()

    env = args.e
    host = conf.HOST[env]
    port = conf.PORT[env]

    run(host=host, port=port, reloader=True, server='gevent', 
            debug=conf.DEBUG, handler_class=WebSocketHandler)
