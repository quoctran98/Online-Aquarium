from flask import copy_current_request_context
from flask_login import current_user
from server.helper import settings, tool_types, authenticated_only

def register_events(socketio, command_queue):

    @socketio.on("connect", namespace="/interactions")
    def connect():
        pass

    @socketio.on("disconnect", namespace="/interactions")
    def disconnect():
        pass

    @socketio.on("tap", namespace="/interactions")
    def tap(data):
        if (current_user.username != data["username"]):
            return
        command_queue.put(("tap", data))

    @socketio.on("pickup", namespace="/interactions")
    def pickup(data):
        if (current_user.username != data["username"]):
            return
        command_queue.put(("pickup", data))

    @socketio.on("use", namespace="/interactions")
    def use(data):
        if (current_user.username != data["username"]):
            return
        tool = tool_types[data["tool"]]
        # Process the transaction and return True if the user can afford the tool
        useAllowed = current_user.process_money(tool["cost"]) 
        if useAllowed: 
            socketio.emit("update_user", current_user.summarize_public, namespace="/interactions")
            # Add the command to the queue
            command_queue.put(("use", data))

    @socketio.on("select", namespace="/interactions")
    def select(data):
        if (current_user.username != data["username"]):
            return
        socketio.emit("select", data, namespace="/interactions")

    @socketio.on("cursor", namespace="/interactions")
    def cursor(data):
        if (current_user.username != data["username"]):
            return
        socketio.emit("cursor", data, namespace="/interactions")
