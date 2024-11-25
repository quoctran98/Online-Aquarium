from flask import request
from flask_login import current_user
from server.helper import settings, authenticated_only, confirm_user
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
    @confirm_user
    def contribute(data):
        store_item = store.items[data["label"]]
        contribution_amount = round(data["amount"], 2)
        if store_item.fully_funded:
            return
        if store_item.money_raised + contribution_amount > store_item.price:
            return # Don't allow overfunding
        if data["amount"] < 0:
            return # Don't allow negative contributions
        contribution_allowed = current_user.subtract_money(contribution_amount)
        if contribution_allowed:
            fully_funded = store.add_contribution(data["label"], data["username"], contribution_amount)
            if fully_funded: # If the item is funded, add it to the aquarium through the command queue
                command_queue.put(("create", {
                    "object_name": store.items[data["label"]].object_name, 
                    "object_kwargs": store.items[data["label"]].object_kwargs,
                    "object_properties": store.items[data["label"]].object_properties
                }))
            # models/store.py will handle resetting the item if it's fully funded and still in stock
            store.save()
            # socketio.emit("update_item", store.items[data["label"]].summarize, namespace="/store") # THIS DOESN'T WORK?
            socketio.emit("summarize_store", store.summarize, namespace="/store") 
