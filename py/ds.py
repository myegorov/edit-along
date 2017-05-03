"""
Differential synchronization logic for server.
"""

from geventwebsocket import WebSocketError
import diff_match_patch as dmp
import json

# TODO: need to synchronize on this one?
CLIENT_FRESH = 0

# TODO: need to synchronize on this one?
# {key=client_id <int>, val={server_shadow <{str,[int,int]}>, backup_shadow <{str, int}>}}
CLIENT_REC = {}
SERVER_TEXT = ""

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
    """Consumer coroutine receives socket connection, route, and message from
    client. Message contains vector clock (array of ints) 
    and JSON-encoded edits (list of [int, str]), in the following format:
        {
          'clock':[<CLIENT_CLOCK>, <SERVER_CLOCK>], # negative on first handshake
          'edits': [[0, 'Mac'], [1, 'intoshe'], \
                    [0, 's had the original point and click '], \
                    [-1, 'UI'], [1, 'interface'], [0, '.']],
          'client_id': int # None on first handshake, hash of client-doc
        }

    Consumer will route the task to the next coroutine:
        - direct to onboard the client if new connection (to existing or
        new document);
        - else check if vector clock is consistent with Server Shadow
        and depending on the outcome: 
            + direct to patch the edits onto the server, or
            + direct to perform one of the failure management scenarios.
    """
    try:
        while True:
            wsock, url, message = (yield)
            # decode message
            message = json.loads(message)
            if message.get('client_id', None) is None: # new client?
                next_step = onboard()
            else:
                rec = CLIENT_REC.get('client_id', None)
                if rec and message.get('clock', [-1,-1]) == \
                   rec['server_shadow'][1]:
                    next_step = patch()
                elif rec:
                    next_step = manage_failure()
                else:
                    raise Exception("consumer() couldn't interpret the message: %s" %message)
            next(next_step)
            next_step.send((wsock, url, message)) # shadowing consumer()

    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        return None
    except StopIteration:
        return None

# TODO: onboard new client
def onboard():
    pass

# TODO: normal operation (steps 5a onwards)
def patch():
    pass

# TODO: address one of error scenarios
def manage_failure():
    pass





# def consumer():

#     # TODO: can identify incoming connection via request.environ dict:
#     # environ['REMOTE_ADDR']
#     # environ['REMOTE_PORT']
#     # print("environ:", wsock.environ)

#     try:
#         while True:
#             wsock, url, message = (yield)
#             wsock.send('Your message was: %r' % message)
#             wsock.send('Your addr is: %s' %(wsock.environ['REMOTE_ADDR']))
#             wsock.send('Your port is: %s' %(wsock.environ['REMOTE_PORT']))
#             wsock.send('Your doc name is: %s' %(url))
#     except WebSocketError:
#         wsock.close()
#     except GeneratorExit:
#         return None
#     except StopIteration:
#         return None


