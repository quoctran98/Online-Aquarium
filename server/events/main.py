from flask import request
from server.helper import settings

def register_events(socketio, command_queue):
    @socketio.on("connect", namespace="/")
    def connect():
        sid = request.sid
        print(f"A user has connected on SocketIO: {sid}")
            
    @socketio.on("disconnect", namespace="/")
    def disconnect():
        sid = request.sid
        print(f"A user has disconnected on SocketIO: {sid}")
