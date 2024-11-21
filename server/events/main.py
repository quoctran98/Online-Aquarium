from flask import request
from server.helper import settings, authenticated_only

def register_events(socketio):

    @socketio.on("connect", namespace="/")
    def connect():
        pass

    @socketio.on("disconnect", namespace="/")
    def disconnect():
        pass
