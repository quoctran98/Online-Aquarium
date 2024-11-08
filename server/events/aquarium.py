from server.helper import settings, authenticated_only
from server.models import Fish

def register_events(socketio, command_queue):
    @socketio.on("connect", namespace="/aquarium")
    def connect():
        # Send the current state of the aquarium to the new client
        command_queue.put("sync")
