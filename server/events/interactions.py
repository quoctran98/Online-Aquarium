from server.helper import settings

def register_events(socketio, command_queue):

    @socketio.on("connect", namespace="/interactions")
    def connect():
        print("A user has connected to the interactions! 🤝")
    
    # So all users can see items moving around
    @socketio.on("pick_up_item", namespace="/interactions")
    def pick_up_item(data):
        print(f"User picked up item {data}")

    @socketio.on("add_fish", namespace="/interactions")
    def add_fish(data):
        print(f"User added fish {data}")
        command_queue.put("add_fish")

    @socketio.on("my_cursor", namespace="/")
    def my_cursor(data):
        # broadcast all cursor movements to all users
        socketio.emit("update_cursor", data)