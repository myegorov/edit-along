from websocket import create_connection
ws = create_connection("ws://129.21.37.42:1070/websocket")
print("sending 'hello world'...")
ws.send("hello world")
print("sent")
print("receving now...")
result = ws.recv()
print("received '%s'" % result)
ws.close()
