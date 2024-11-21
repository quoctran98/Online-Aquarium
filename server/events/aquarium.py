from server.helper import settings, authenticated_only
from server.models.aquarium import Fish

def register_events(socketio, command_queue):
    @socketio.on("connect", namespace="/aquarium")
    def connect():
        # Send the current state of the aquarium to the new client (all clients)
        command_queue.put(("sync", None))

    @socketio.on("disconnect", namespace="/aquarium")
    def disconnect():
        pass