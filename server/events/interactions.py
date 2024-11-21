from flask import copy_current_request_context
from flask_login import current_user
from server.helper import settings, tool_types, authenticated_only, confirm_user

def register_events(socketio, command_queue):

    @socketio.on("connect", namespace="/interactions")
    def connect():
        pass

    @socketio.on("disconnect", namespace="/interactions")
    def disconnect():
        pass

    @socketio.on("tap", namespace="/interactions")
    @confirm_user
    def tap(data):
        command_queue.put(("tap", data))
        socketio.emit("tap", data, namespace="/interactions")

    @socketio.on("pickup", namespace="/interactions")
    @confirm_user
    def pickup(data):
        command_queue.put(("pickup", data))
        socketio.emit("pickup", data, namespace="/interactions")

    @socketio.on("click", namespace="/interactions")
    @confirm_user
    def click(data):
        command_queue.put(("click", data))
        socketio.emit("click", data, namespace="/interactions")

    @socketio.on("use", namespace="/interactions")
    @confirm_user
    def use(data):
        tool = tool_types[data["tool"]]
        # Process the transaction and return True if the user can afford the tool
        useAllowed = current_user.subtract_money(tool["cost"]) 
        if useAllowed: 
            # Update the user's money!
            socketio.emit("update_user", current_user.summarize_public, namespace="/interactions")
            # Add the command to the queue
            command_queue.put(("use", data))
            # Also rebroadcast the tool use
            socketio.emit("use", data, namespace="/interactions")

    @socketio.on("select", namespace="/interactions")
    @confirm_user
    def select(data):
        socketio.emit("select", data, namespace="/interactions")

    @socketio.on("cursor", namespace="/interactions")
    @confirm_user
    def cursor(data):
        socketio.emit("cursor", data, namespace="/interactions")
