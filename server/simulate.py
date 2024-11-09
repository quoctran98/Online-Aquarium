from flask_socketio import emit
from server.helper import settings
from server.game_models import Fish, Aquarium
from datetime import datetime, timezone
import time

# Move this to a config file later
SIMULATION_TICK = 0.05 # seconds per tick
SYNC_FREQUENCY = 1 # seconds per sync
BACKUP_FREQUENCY = 300 # seconds per backup

# This is the main game/simulation loop
# Either pass an existing aquarium or create a new one
def aquarium_simulation(socketio, command_queue, aquarium = Aquarium("fishbowl")):
    
    last_loop = datetime.now(timezone.utc)
    last_sync = datetime.now(timezone.utc)
    last_backup = datetime.now(timezone.utc)

    # Give it one free fish for debugging
    fish = Fish(type="goldfish", aquarium=aquarium)
    aquarium.fishes.append(fish)

    while True:

        # Start a timer and calculate the time since the last loop
        loop_start = datetime.now(timezone.utc)
        delta_time = loop_start - last_loop
      
        # Check if there are any commands in the queue
        if not command_queue.empty():
            command = command_queue.get()
            match command:
                case "add_fish":
                    fish = Fish(type="goldfish", aquarium=aquarium)
                    aquarium.fishes.append(fish)
                case "sync":
                    socketio.emit("sync_fishes", [fish.summarize for fish in aquarium.fishes], namespace="/aquarium")
                case _:
                    Warning(f"Unknown command {command}")

        # Update all fishes in the aquarium (and broadcast the changes)
        for fish in aquarium.fishes:
            changed = fish.update(delta_time)
            if changed:
                socketio.emit("update_fish", fish.summarize, namespace="/aquarium")

        # Every few seconds (SYNC_FREQUENCY), sync the current state of the aquarium to with all clients
        if (loop_start - last_sync).total_seconds() > SYNC_FREQUENCY:
            last_sync = loop_start
            socketio.emit("sync_fishes", [fish.summarize for fish in aquarium.fishes], namespace="/aquarium")

        # Every few minutes (BACKUP_FREQUENCY), save the current state of the aquarium
        if (loop_start - last_backup).total_seconds() > BACKUP_FREQUENCY:
            last_backup = loop_start
            aquarium.save(settings.AQUARIUM_SAVE_DIR)
            print(f"Backup saved at {last_backup}")

        # Calculate the time it took to run the loop and wait for the next tick
        loop_end = datetime.now(timezone.utc)
        last_loop = loop_end
        loop_time = (loop_end - loop_start).total_seconds()
        if loop_time > SIMULATION_TICK:
            Warning(f"Loop took {loop_time} seconds, which is longer than the tick time of {SIMULATION_TICK} seconds")
        time.sleep(max(0, SIMULATION_TICK - loop_time))
