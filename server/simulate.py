from flask_socketio import SocketIO, emit
from server.helper import settings
from server.models import Fish, Aquarium
from datetime import datetime, timezone
import time

# This is the main game/simulation loop
# Either pass an existing aquarium or create a new one
def aquarium_simulation(socketio, command_queue, aquarium = Aquarium("fishbowl")):
    last_update = datetime.now(timezone.utc)
    while True:

        # Do timing things
        loop_start = datetime.now(timezone.utc)
        delta_time = loop_start - last_update
      
        # Check if there are any commands in the queue
        if not command_queue.empty():
            command = command_queue.get()
            print(command)
            match command:
                case "add_fish":
                    fish = Fish(type="goldfish", aquarium=aquarium)
                    aquarium.fishes.append(fish)
                case _:
                    Warning(f"Unknown command {command}")

        # Update all fishes in the aquarium
        for fish in aquarium.fishes:
            fish.update(delta_time)

        # Broadcast the current state of all fishes in the aquarium
        socketio.emit("updateFishes", [fish.serialize for fish in aquarium.fishes])

        # Calculate the time it took to run the loop
        loop_end = datetime.now(timezone.utc)
        last_update = loop_end
        # Wait for the next tick
        time.sleep(max(0, settings.SIMULATION_TICK - (loop_end - loop_start).total_seconds()))
