"""
Differential synchronization logic for server.
"""
# TODO: edits actually may be a stack (array of string patches)!!!
# TODO: decide on whether to pass around diffs or patches?? diffs seems
# safer on average, but patches more economical?? Currently shooting for
# sending patches over network.
#   'edits': [[0, 'Mac'], [1, 'intoshe'], \
#             [0, 's had the original point and click '], \
#             [-1, 'UI'], [1, 'interface'], [0, '.']],
# or
#   'edits': ["""@@ -1,11 +1,18 @@
              #  Mac
              # +intoshe
              # s had th
              # @@ -42,7 +42,14 @@
              # ick
              # -UI
              # +interface
              # ."""]



from geventwebsocket import WebSocketError
import diff_match_patch as dmp
import json

# TODO: need to synchronize on this one?
# {key=client_id <int>, val={server_shadow <{str,[int,int]}>, backup_shadow <{str, int}>}}
CLIENT_REC = {}
# {key=doc_id<int>, val=server_text<str>}
SERVER_TEXT = {}

diffy = dmp.diff_match_patch()

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

def onboard():
    """Onboard new client, then on to normal operations."""
    try:
        wsock, url, message = (yield)

        # get fresh client id (a hash on doc-client pair)
        doc_id = url.rstrip('/').split('/')[-1]
        ip = wsock.environ['REMOTE_ADDR']
        client_id = hash(doc_id+ip)

        # check if server_text exists for given doc_id
        # do the minimal setup, then on to normal operation
        # get fresh server text if it doesn't exist already
        server_text = SERVER_TEXT.setdefault(doc_id, '')

        clock = message.get('clock', None) # consistency check
        assert clock == [-1,-1], \
            "onboard() found inconsistent clock on handshake: %s" %message
        server_shadow = {'text':server_text, 'clock': clock[:]} # initially [-1,-1]
        backup_shadow = {'text':server_text, 'server_clock':clock[1]}
        CLIENT_REC[client_id] = {'server_shadow':server_shadow, 
                                'backup_shadow':backup_shadow}
        # should be OK if edits are empty
        edits = message.get('edits', ['']) # edits are a list of patch strings

        # move on now
        normal_ops = patch()
        next(normal_ops)
        normal_ops.send((wsock, url, {'clock':clock, 
                                    'edits':edits,
                                    'client_id':client_id}))

    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        return None
    except StopIteration:
        return None


# TODO: normal operation (steps 5a onwards)
def patch():

    # # {key=client_id <int>, val={server_shadow <{str,[int,int]}>, backup_shadow <{str, int}>}}
    # CLIENT_REC = {}

    # # {key=doc_id<int>, val=server_text<str>}
    # SERVER_TEXT = {}

    # {
    #   'clock':[<CLIENT_CLOCK>, <SERVER_CLOCK>], # negative on first handshake
    #   'edits': "@@ -1,11 +1,18 @@\n Mac\n+intoshe\n s had th\n@@ -42,7 +42,14 @@\n ick \n-UI\n+interface\n .\n",
    #   'client_id': int # None on first handshake, hash of client-doc
    # }



    wsock, url, message = (yield)


    # edits = message.get('edits', None)
    # if edits is not None:
    #     server_text = diffy.patch_apply(diffy.patch_fromText(edits), '')


    pass

# TODO: address one of error scenarios
def manage_failure():
    wsock, url, message = (yield)
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


