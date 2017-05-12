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

# (2) mimick client never received response from server
ws = create_connection(url)

delta = dmp_exact.diff_main('', 'asdf') # old, new
patches = dmp_exact.patch_make('', delta)
patch_txt = dmp_exact.patch_toText(patches)
new_msg = json.dumps({'clock': [0,-1],
                      'edits': patch_txt,
                      'client_id':client_id})
print("client sends [MISSING UPDATE]: '%s'" %json.loads(new_msg))
ws.send(new_msg)
res = json.loads(ws.recv())
print("client received: '%s'" %(res))
ws.close()
