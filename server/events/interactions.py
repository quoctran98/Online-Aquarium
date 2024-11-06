from flask import request
from server.helper import settings

def register_events(socketio, command_queue):

    @socketio.on("connect", namespace="/interactions")
    def connect():
        pass

    @socketio.on("disconnect", namespace="/interactions")
    def disconnect():
        # Broadcast the disconnect to all users (for cursor purposes only for now)
        socketio.emit("user_disconnected", request.sid, namespace="/interactions")
    
    # So all users can see items moving around
    @socketio.on("pick_up_item", namespace="/interactions")
    def pick_up_item(data):
        print(f"User picked up item {data}")

    @socketio.on("add_fish", namespace="/interactions")
    def add_fish(data):
        print(f"User added fish {data}")
        command_queue.put("add_fish")

    @socketio.on("my_cursor", namespace="/interactions")
    def my_cursor(data):
        # Broadcast all cursor movements to all users
        socketio.emit("update_cursor", data, namespace="/interactions")