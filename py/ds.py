"""
Differential synchronization logic for server.
"""
# TODO: make edits a queue
# TODO: substitute diffs for patches? otoh patches seem more succinct?

from geventwebsocket import WebSocketError
import diff_match_patch as dmp
import json
from hashlib import md5

# {key=client_id <str>, val={server_shadow <{str,[int,int]}>, backup_shadow <{str, int}>}}
CLIENT_REC = {}
# {key=doc_id<str>, val=server_text<str>}
SERVER_TEXT = {}



# TODO: make outgoing and incoming queues fields
# of CLIENT_REC, so they can be accessed per client
# [message0, ... , messagen]
# Each message is a JSON dump of a dict such as this:
# {
#   'clock':[<CLIENT_CLOCK_USED>, <SERVER_CLOCK_USED>],
#   'edits': "@@ -1,11 +1,18 @@\n Mac\n+intoshe\n s had th\n@@ -42,7 +42,14 @@\n ick \n-UI\n+interface\n .\n",
#   'client_id': some_str # None on first handshake, hash of client-doc
# }
INCOMING_QUEUE = [] # queue of out-of-order packets
OUTGOING_QUEUE = []

dmp_fuzzy = dmp.diff_match_patch(0.4) # fuzzy Match_Threshold
dmp_exact = dmp.diff_match_patch(0.0) # specify Match_Threshold for perfect match

def hash(string):
    """Built-in hash() function returns different hashes on different
    invocations of interpreter unless env variable PYTHONHASHSEED=0 is set.

    Arguments:
        string (str): some string identifying client-document combination,
                        kept consistent from one session to another. 7 chars
                        should be enough for the toy example.

    Returns:
        hash (str)
    """
    return md5(string.encode('utf-8')).hexdigest()[:7]


def conveyor_belt(consumer):
    """ An entry point coroutine that adds socket requests to 
    the consumer() coroutine.
    """
    try:
        while True:
            wsock, url = (yield)
            message = wsock.receive()
            # if null message, ignore
            if message is None:
                return
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
          'edits': '@@ -1,11 +1,18 @@\n Mac\n+intoshe\n s had th\n@@ -42,7 +42,14 @@\n ick \n-UI\n+interface\n .\n',
          'client_id': str # None on first handshake, hash of client-doc
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
            client_id = message.get('client_id', None)
            if client_id is None: # new client?
                next_step = onboard()
            else:
                rec = CLIENT_REC.get(client_id, None)
                if rec and message.get('clock', [-1,-1]) == \
                   rec['server_shadow'].get('clock'):
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
        port = wsock.environ['REMOTE_PORT'] # distinguish between clients on same host
        client_id = hash(doc_id+ip+':'+port)

        # check if server_text exists for given doc_id
        # do the minimal setup, then on to normal operation
        # get fresh server text if it doesn't exist already
        server_text = SERVER_TEXT.setdefault(doc_id, '')

        clock = message.get('clock', None) # consistency check
        assert clock == [-1,-1], \
            "onboard() found inconsistent clock on handshake: %s" %message
        # set up new shadow & backup copies per client connection
        server_shadow = {'text':'', 'clock': clock[:]} # initially [-1,-1]
        backup_shadow = {'text':'', 'server_clock':clock[1]}

        CLIENT_REC[client_id] = {'server_shadow':server_shadow, 
                                'backup_shadow':backup_shadow}
        # should be OK if edits are empty
        edits = message.get('edits', '') # edits are a list of patch strings

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


def patch():
    """Normal operation (steps 5a onwards)."""
    try:
        wsock, url, message = (yield)

        edit = message['edits']
        doc_id = url.rstrip('/').split('/')[-1]

        # if new client is joining with existing doc_id
        # client sends edits == ''; client should just
        # get a copy of server text, __not__ overwrite server text.
        server_text = SERVER_TEXT[doc_id]
        server_shadow = CLIENT_REC[message['client_id']]['server_shadow']
        clock = server_shadow['clock']
        init = message.get('init', False) # is new client joining?
        sync = message.get('sync', False) # is old cliend just querying for server updates?
        txt_ = '' if init else server_shadow['text']
        txt__ = server_text

        backup_shadow = CLIENT_REC[message['client_id']]['backup_shadow']
        if edit != '' and not (sync or init):
            # exact patch of Server Shadow
            # also, snapshot Server Shadow into Backup Shadow
            txt = server_shadow['text']
            txt_ =  dmp_exact.patch_apply(dmp_exact.patch_fromText(edit), txt)[0]

            backup_shadow = {'text':txt_, 'server_clock':clock[1]}

            # fuzzy patch onto Server Text
            txt__ = dmp_fuzzy.patch_apply(dmp_fuzzy.patch_fromText(edit), server_text)[0]
            SERVER_TEXT[doc_id] = txt__

        # update client's clock record
        clock[0] += 1
        # create diff -> patch off of Server Text and Server Shadow
        delta = dmp_exact.diff_main(txt_, txt__) # old, new
        patches = dmp_exact.patch_make(txt_, delta)
        patch_txt = dmp_exact.patch_toText(patches)



        # compose message and add to outgoing queue
        msg_to_client = {'clock':clock[:], 
                        'edits':patch_txt, 
                        'client_id':message['client_id']}
        OUTGOING_QUEUE.append(json.dumps(msg_to_client))

        # increment server clock and snapshot Server Text into Server Shadow
        clock[1] += 1
        server_shadow_ = {'text':txt__, 'clock': clock[:]}
        CLIENT_REC[message['client_id']] = \
                                {'server_shadow':server_shadow_, 
                                'backup_shadow':backup_shadow}

        # yield control to mailman coroutine
        deliver = mailman()
        next(deliver)
        deliver.send(wsock)

    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        return None
    except StopIteration:
        return None



def mailman():
    """Deliver a message to client & discard the message. 
    No need to keep message in outgoing queue, unlike with 
    Client's outgoing queue."""

    try:
        wsock = (yield)
        # in principle, shouldn't be here if queue empty
        if wsock is not None and len(OUTGOING_QUEUE) > 0:
            wsock.send(OUTGOING_QUEUE.pop(0))
        # presently not maintaining connection, left for the future...
        wsock.close()

    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        return None
    except StopIteration:
        return None


# TODO: address error scenarios
def manage_failure():
    try:
        wsock, url, message = (yield)

        clock_received = message.get('clock', None)
        server_shadow = CLIENT_REC[message['client_id']]['server_shadow']
        backup_shadow = CLIENT_REC[message['client_id']]['backup_shadow']
        clock_shadow = server_shadow['clock']
        clock_backup = backup_shadow['server_clock']
        doc_id = url.rstrip('/').split('/')[-1]
        server_text = SERVER_TEXT[doc_id]

        # (1) duplicate packet
        if clock_shadow[0] > clock_received[0]:
            # compose message and add to outgoing queue
            msg_to_client = {'clock':clock_shadow[:], 
                            'edits':'',
                            'client_id':message['client_id'],
                            'duplicate':True}
            OUTGOING_QUEUE.append(json.dumps(msg_to_client))

            # yield control to mailman coroutine
            deliver = mailman()
            next(deliver)
            deliver.send(wsock)
        # (2) lost on return: client never received msg from server
        elif clock_backup == clock_received[1] and \
            clock_shadow[1] > clock_received[1] and \
            clock_shadow[0] == clock_received[0]:

            # TODO: should check if outgoing queue contains delayed
            # message -> if so, delete it!

            # restore server shadow, update client's clock
            clock_reset = [clock_received[0]+1, clock_backup]

            txt = backup_shadow['text']

            # now compute and transmit a fresh diff to the client
            # create diff -> patch off of Server Text and reset Server Shadow
            delta = dmp_exact.diff_main(txt, server_text) # old, new
            patches = dmp_exact.patch_make(txt, delta)
            patch_txt = dmp_exact.patch_toText(patches)

            # compose message and add to outgoing queue
            msg_to_client = {'clock':clock_reset[:], 
                             'edits':patch_txt, 
                             'client_id':message['client_id'],
                             'lost_return':True}
            OUTGOING_QUEUE.append(json.dumps(msg_to_client))

            # increment server clock and snapshot Server Text into Server Shadow
            # no updates to backup shadow in this scenario
            clock_reset[1] += 1
            updated_server_shadow = {'text':server_text, 'clock': clock_reset[:]}
            CLIENT_REC[message['client_id']]['server_shadow'] = \
                    updated_server_shadow

            # yield control to mailman coroutine
            deliver = mailman()
            next(deliver)
            deliver.send(wsock)

        # TODO: (3) other failure scenarios, ditto on client side
        # for now just force reinitialization of client's data
        # meaning data loss for client...
        else:
            reset = True

            # now compute and transmit a fresh diff to the client
            # create diff -> patch off of Server Text and reset Server Shadow
            txt = '' # as if client is joining TODO in the future merge this logic with onboard()
            delta = dmp_exact.diff_main(txt, server_text) # old, new
            patches = dmp_exact.patch_make(txt, delta)
            patch_txt = dmp_exact.patch_toText(patches)

            # compose message and add to outgoing queue
            msg_to_client = {'clock':clock_shadow[:], 
                             'edits':patch_txt, 
                             'client_id':message['client_id'],
                             'reset':True}
            OUTGOING_QUEUE.append(json.dumps(msg_to_client))

            # increment server clock and snapshot Server Text into Server Shadow
            # no updates to backup shadow in this scenario
            clock_shadow[1] += 1
            updated_server_shadow = {'text':server_text, 'clock': clock_shadow[:]}
            CLIENT_REC[message['client_id']]['server_shadow'] = \
                    updated_server_shadow

            # yield control to mailman coroutine
            deliver = mailman()
            next(deliver)
            deliver.send(wsock)


    except WebSocketError:
        wsock.close()
    except GeneratorExit:
        return None
    except StopIteration:
        return None
