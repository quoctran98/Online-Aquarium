from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only
import datetime

def register_events(socketio, command_queue, store):

    @socketio.on("connect", namespace="/store")
    def connect():
        pass

    @socketio.on("disconnect", namespace="/store")
    def disconnect():
        pass

    @socketio.on("get_store", namespace="/store")
    def summarize_store():
        socketio.emit("summarize_store", store.summarize, namespace="/store")

    @socketio.on("contribute", namespace="/store")
    def contribute(data):
        username = current_user.username
        if current_user.username != data["username"]:
            return
        store_item = store.items[data["label"]]
        if store_item.fully_funded:
            return
        # if store_item.money_raised + data["amount"] > store_item.price:
        #     return # Don't allow overfunding
        # Allow it for now as a bandaid!
        if data["amount"] < 0:
            return # Don't allow negative contributions
        contribution_amount = round(data["amount"], 2)
        contribution_allowed = current_user.process_money(contribution_amount)
        if contribution_allowed:
            fully_funded = store.add_contribution(data["label"], data["username"], contribution_amount)
            if fully_funded: # If the item is funded, add it to the aquarium through the command queue
                command_queue.put(("add", {
                    "object_name": store.items[data["label"]].object_name, 
                    "object_kwargs": store.items[data["label"]].object_kwargs,
                    "object_properties": store.items[data["label"]].object_properties
                }))

            # socketio.emit("update_item", store.items[data["label"]].summarize, namespace="/store") # THIS DOESN'T WORK?
            socketio.emit("summarize_store", store.summarize, namespace="/store") 
            store.save()
