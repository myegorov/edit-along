""" Python client to test websocket server.
"""


import conf
from websocket import create_connection
import time

host = conf.HOST['DEV']
port = conf.PORT['DEV']

# ws = create_connection("ws://129.21.37.42:1070/websocket/dummy_url")
url = 'ws://' + host + ':' + str(port) + '/websocket/' + 'dummy_url'
ws = create_connection(url)


print("sending 'hello world'...")
ws.send("hello world")
print("sent...")
# time.sleep(3)
print("receving now...")
result = ws.recv()
print("received '%s'" % result)
ws.close()
