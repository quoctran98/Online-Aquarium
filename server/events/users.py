from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only

def register_events(socketio, user_manager):
    @socketio.on("connect", namespace="/users")
    def connect():
        # Add the user to the user_manager (not the best way to do this but it works)
        user_manager.user_connected(current_user)
        socketio.emit("user_connected", current_user.summarize_public, namespace="/users")
            
    @socketio.on("disconnect", namespace="/users")
    def disconnect():
        # Remove the user from the user_manager
        user_manager.user_disconnected(current_user)
        socketio.emit("user_disconnected", current_user.summarize_public, namespace="/users")
