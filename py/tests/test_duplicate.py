""" Python client to test websocket server.
"""

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import json
import diff_match_patch as dmp

import conf
from websocket import create_connection
import time


dmp_fuzzy = dmp.diff_match_patch(0.4) # fuzzy Match_Threshold
dmp_exact = dmp.diff_match_patch(0.0) # specify Match_Threshold for perfect match

host = conf.HOST['DEV']
port = conf.PORT['DEV']

# ws = create_connection("ws://129.21.37.42:1070/websocket/dummy_url")
url = 'ws://' + host + ':' + str(port) + '/websocket/' + 'some_url'
ws = create_connection(url)


# (1) initial message to server
init_msg = json.dumps({'clock': [-1,-1],
            'edits': '',
            'client_id':None,
            'init': True})
print("client sends: '%s'" %json.loads(init_msg))
ws.send(init_msg)
res = json.loads(ws.recv())
ws.close()

client_id = res['client_id']
clock_received = res['clock']

# (2) duplicate send
ws = create_connection(url)
duplicate_msg = json.dumps({'clock': [-1,-1],
                            'edits': '',
                            'client_id':client_id,
                            'init': True})
print("client sends [DUPLICATE]: '%s'" %json.loads(duplicate_msg))
ws.send(duplicate_msg)
res = json.loads(ws.recv())
print("client received: '%s'" %(res))
ws.close()
