from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only
import datetime

def register_events(socketio, command_queue, store):

    @socketio.on("connect", namespace="/store")
    def connect():
        print(f"🛒 User {current_user.username} conneected to the store!")
        socketio.emit("summarize_store", [item.summarize for item in store.items.values()], namespace="/store")

    @socketio.on("disconnect", namespace="/store")
    def disconnect():
        pass

    @socketio.on("get_store", namespace="/store")
    def summarize_store():
        print(f"🛒 User {current_user.username} requested store summary")
        socketio.emit("summarize_store", [item.summarize for item in store.items.values()], namespace="/store")

    @socketio.on("contribute", namespace="/store")
    def contribute(data):
        username = current_user.username
        if current_user.username != data["username"]:
            return
        contributionAllowed = current_user.process_money(data["amount"])
        if contributionAllowed:
            store.add_contribution(data["label"], data["username"], data["amount"])
            # socketio.emit("update_item", store.items[data["label"]].summarize, namespace="/store") # THIS DOESN'T WORK?
            socketio.emit("summarize_store", [item.summarize for item in store.items.values()], namespace="/store") 
            store.save(settings.STORE_SAVE_DIR)
