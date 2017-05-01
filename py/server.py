# TODO: can identify incoming connection via request.environ dict:
# environ['REMOTE_ADDR']
# environ['REMOTE_PORT']


from bottle import Bottle, route, run, get, static_file, request, abort

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError


host = '127.0.0.1'
port = 8080
# app = Bottle()

# @app.route('/')
@route('/')
def index():
    return static_file('index.html', root="../")

# @app.get("/static/css/<filepath:re:.*\.css>")
@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="../static/css")

# @app.get("/static/js/<filepath:re:.*\.js>")
@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="../static/js")

# @app.route('/websocket')
@route('/websocket')
def socks():
    wsock = request.environ.get('wsgi.websocket')
    # print("environ:", wsock.environ)

    if not wsock:
        abort(400, 'Expected websocket request...')
    while True:
        try:
            message = wsock.receive()
            wsock.send('Your message was: %r' % message)
        except WebSocketError:
            break


run(host=host, port=port, reloader=True, server='gevent', 
        debug=True, handler_class=WebSocketHandler)

# server = WSGIServer((host, port), app,
#                     handler_class=WebSocketHandler)
# print("access @ http://%s:%s/" %(host, port))
# server.serve_forever()
