import zmq
import cv2
import json
import uuid

def getContext():
    return zmq.Context()

def getSocket(context):
    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, uuid.uuid4().bytes)
    socket.setsockopt(zmq.LINGER,0)
    socket.connect("tcp://localhost:5555")
    return socket

def getPoseFromImage(socket, image ):
    encoded = cv2.imencode(".jpg",image)
    socket.send_multipart([b"",encoded[1].tostring()])
    #socket.send(encoded[1].tostring())
    print("Sending request")
    message = socket.recv()
    #print("Received reply %s :"% message)

    data = json.loads(message.decode("utf-8") )
    return data



def ProcessZmq( socket,test ):
    socket.send_multipart([b"A",test.encode("utf-8")])
    print("Sending request")
    reply = socket.recv()
    print("Received reply %s :" % reply)
    #message = socket.recv()
    #print("Received reply %s :"% message)




