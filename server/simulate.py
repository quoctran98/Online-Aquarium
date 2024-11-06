from flask_socketio import emit
from server.helper import settings
from server.models import Fish, Aquarium
from datetime import datetime, timezone
import time

SIMULATION_TICK = settings.SIMULATION_TICK # seconds per tick
SYNC_FREQUENCY = 1 # seconds per sync

# This is the main game/simulation loop
# Either pass an existing aquarium or create a new one
def aquarium_simulation(socketio, command_queue, aquarium = Aquarium("fishbowl")):
    last_loop = datetime.now(timezone.utc)
    last_sync = datetime.now(timezone.utc)
    while True:

        # Do timing things
        loop_start = datetime.now(timezone.utc)
        delta_time = loop_start - last_loop
      
        # Check if there are any commands in the queue
        if not command_queue.empty():
            command = command_queue.get()
            match command:
                case "add_fish":
                    fish = Fish(type="goldfish", aquarium=aquarium)
                    aquarium.fishes.append(fish)
                case _:
                    Warning(f"Unknown command {command}")

        # Update all fishes in the aquarium (and broadcast the changes)
        for fish in aquarium.fishes:
            changed = fish.update(delta_time)
            if changed:
                socketio.emit("update_fish", fish.summarize, namespace="/aquarium")

        # Broadcast the current state of all fishes in the aquarium (every few seconds to sync)
        if (loop_start - last_sync).total_seconds() > SYNC_FREQUENCY:
            last_sync = loop_start
            socketio.emit("sync_fishes", [fish.summarize for fish in aquarium.fishes], namespace="/aquarium")

        # Calculate the time it took to run the loop
        loop_end = datetime.now(timezone.utc)
        last_loop = loop_end
        # Wait for the next tick
        time.sleep(max(0, SIMULATION_TICK - (loop_end - loop_start).total_seconds()))
