from server.helper import settings
from server.models import Fish

def register_events(socketio, command_queue):
    @socketio.on("connect", namespace="/aquarium")
    def connect():
        print("A user has connected to the aquarium! 🐠")
            
    @socketio.on("disconnect")
    def disconnect():
        print("A user has disconnected! 😢")
