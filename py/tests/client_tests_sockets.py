""" Python client to test websocket server.
"""

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import json
import diff_match_patch as dmp

import conf
from websocket import create_connection
import time

host = conf.HOST['DEV']
port = conf.PORT['DEV']

# ws = create_connection("ws://129.21.37.42:1070/websocket/dummy_url")
url = 'ws://' + host + ':' + str(port) + '/websocket/' + 'some_url'
ws = create_connection(url)


dmp_exact = dmp.diff_match_patch(0.0) # specify Match_Threshold for perfect match
delta = dmp_exact.diff_main('', 'asdf') # old, new
patches = dmp_exact.patch_make('', delta)
patch_txt = dmp_exact.patch_toText(patches)
message = json.dumps({'clock':[-1,-1],'edits':patch_txt, 'client_id':None}) 
# message = json.dumps({'clock':[-1,-1],'edits':patch_txt, 'client_id':'10dbbbf'}) 

# print("sending 'hello world'...")
print("sending message: %s..." %json.loads(message))
ws.send(message)
print("sent...")
# time.sleep(3)
print("receving now...")
result = ws.recv()
print("received '%s'" % json.loads(result))
ws.close()
