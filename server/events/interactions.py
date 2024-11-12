from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only

def register_events(socketio, command_queue):

    @socketio.on("connect", namespace="/interactions")
    def connect():
        username = request.args.get("username")
        # Broadcast the connect to all users (for cursor purposes only for now)
        socketio.emit("user_connected", username, namespace="/interactions")

    @socketio.on("disconnect", namespace="/interactions")
    def disconnect():
        username = request.args.get("username")
        # Broadcast the disconnect to all users (for cursor purposes only for now)
        socketio.emit("user_disconnected", username, namespace="/interactions")
    
    # So all users can see items moving around
    @socketio.on("pick_up_item", namespace="/interactions")
    def pick_up_item(data):
        print(f"User picked up item {data}")

    @socketio.on("click", namespace="/interactions")
    def click(data):
        username = current_user.username
        command_queue.put(("click", data))

    @socketio.on("feed", namespace="/interactions")
    def feed(data):
        username = current_user.username
        print(f"{username} added food at {data}")
        command_queue.put(("feed", data))

    @socketio.on("my_cursor", namespace="/interactions")
    def my_cursor(data):
        # Broadcast all cursor movements to all users
        socketio.emit("update_cursor", data, namespace="/interactions")
