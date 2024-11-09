from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only

def register_events(socketio, command_queue):

    @socketio.on("connect", namespace="/chat")
    def connect():
        username = current_user.username
        print(f"☃️ User connected: {username}")
        # Broadcast the connect to all users 
        socketio.emit("user_connected", username, namespace="/chat")

    @socketio.on("disconnect", namespace="/chat")
    def disconnect():
        username = request.args.get("username")
        # Broadcast the disconnect to all users
        socketio.emit("user_disconnected", username, namespace="/chat")

    @socketio.on("new_message", namespace="/chat")
    def new_message(data):
        # Broadcast all cursor movements to all users
        socketio.emit("new_message", data, namespace="/chat")
