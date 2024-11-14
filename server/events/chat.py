from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only, sanitize_message
import datetime

def register_events(socketio, chat_manager):

    @socketio.on("connect", namespace="/chat")
    def connect():
        pass

    @socketio.on("disconnect", namespace="/chat")
    def disconnect():
        pass

    @socketio.on("new_message", namespace="/chat")
    def new_message(data):
        print(f"📬 New message from {current_user.username}: {data['message']}")
        # Replace timestamp with the current time (ms since epoch)
        data["timestamp"] = datetime.datetime.now().timestamp() * 1000
        # Sanitize the message
        data["message"] = sanitize_message(data["message"])
        # Broadcast all cursor movements to all users
        socketio.emit("new_message", data, namespace="/chat")
