from server.helper import settings
from server.models import Fish

def register_events(socketio, command_queue):
    @socketio.on("connect")
    def connect():
        print("A user has connected! 🎉")
            
    @socketio.on("disconnect")
    def disconnect():
        print("A user has disconnected! 😢")

    @socketio.on("message")
    def message(data):
        print(f"Received message: {data}")

        if data == "add_fish":
            command_queue.put("add_fish")          
