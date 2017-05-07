"""
run with
    python3 server.py -e <ENV>
"""


from bottle import Bottle, route, run, get, static_file, request, abort, redirect, debug, error, hook

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

from ds import conveyor_belt, consumer
import conf

import argparse
from random import choice
from string import ascii_lowercase, digits


RAND_URL_LENGTH = 5

@hook('before_request')
def strip_path():
    """Preprocess URLs to be routed to /w/some_doc
    """
    raw_url = request.environ['PATH_INFO']
    tmp = raw_url.lstrip('/').split('/')
    if len(tmp) > 2 and tmp[0].lower() == 'w':
        redirect('/'+'/'.join(tmp[:2]))

@get('/')
def index():
    # create a random url
    pth = '/w/'+''.join(choice(ascii_lowercase+digits) for i in range(RAND_URL_LENGTH))
    redirect(pth)

@get('/w/<url:re:.+>')
def doc(url):
    # request.environ['PATH_INFO'] = '/'.join(request.environ['PATH_INFO'].split('/')[:3])
    # print('made:', request.url)
    return static_file('index.html', root="../")

@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="../static/css")

@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="../static/js")

@get("/websocket/<url:re:.+>")
def socks(url=None):
    wsock = request.environ.get('wsgi.websocket')


    # print ('got websocket request with signature:', request.environ)

    #TODO: set cookie on a client?
    # schmeditor = int(request.cookies.get('schmeditor', random.randint()))
    # response.set_cookie('schmeditor', str(schmeditor))

    if not wsock:
        abort(400, 'Expected websocket request...')
    else:
        try:
            task_queue = conveyor_belt(consumer)
            next(task_queue)
            while True:
                # put the packet onto conveyor belt of tasks to do --
                # an entry-point coroutine within ds pipeline
                task_queue.send((wsock, url))
        except StopIteration:
            task_queue.close()
        except WebSocketError:
            wsock.close()

@get("<url:re:.+>")
def catch_all_route(url):
    # print("got: ", request.environ['PATH_INFO'])
    redirect('/')

if __name__ == "__main__":
    """Start a passive socket. Parse CLI arguments for environment."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", type=str, default='DEV', help="one of ['DEV', 'PROD']")
    args = parser.parse_args()

    env = args.e
    host = conf.HOST[env]
    port = conf.PORT[env]
    debug(conf.DEBUG)

    run(host=host, port=port, reloader=True, server='gevent', 
            debug=conf.DEBUG, handler_class=WebSocketHandler)
