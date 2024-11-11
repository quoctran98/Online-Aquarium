from flask_socketio import emit
from server.helper import settings
from server.models.game import Fish, Aquarium, Coin, Food
from server.models.fish import Guppy, Goldfish
from datetime import datetime, timezone
import time, random

# Move this to a config file later
SIMULATION_TICK = 0.05 # seconds per tick
SYNC_FREQUENCY = 1 # seconds per sync
BACKUP_FREQUENCY = 300 # seconds per backup

# This is the main game/simulation loop
# Either pass an existing aquarium or create a new one
def aquarium_simulation(socketio, command_queue, aquarium = Aquarium()):
    
    last_loop = datetime.now(timezone.utc)
    last_sync = datetime.now(timezone.utc)
    last_backup = datetime.now(timezone.utc)

    # Give it two free fish for debugging
    guppy = Guppy(aquarium)
    aquarium.objects[guppy.label] = guppy
    goldfish =  Goldfish(aquarium)
    aquarium.objects[goldfish.label] = goldfish

    while True:

        # Start a timer and calculate the time since the last loop
        loop_start = datetime.now(timezone.utc)
        delta_time = loop_start - last_loop
      
        # Check if there are any commands in the queue
        if not command_queue.empty():
            command, data = command_queue.get()
            match command:
                # case "add_fish":
                #     fish = Fish(type="goldfish", aquarium=aquarium)
                #     aquarium.fishes.append(fish)
                case "add_food":
                    food = Food(aquarium, x=data["x"], y=data["y"])
                    aquarium.objects[food.label] = food
                    socketio.emit("update_thing", food.summarize, namespace="/aquarium")
                case "sync":
                    socketio.emit("sync_everything", [thing.summarize for thing in aquarium.objects.values()], namespace="/aquarium")
                case _:
                    Warning(f"Unknown command {command}")

        # Update all Things in the aquarium
        things_to_iterate = list(aquarium.objects.values()) # Prevent the dict from changing size during iteration
        for thing in things_to_iterate:
            changed = thing.update(delta_time)
            if changed:
                socketio.emit("update_thing", thing.summarize, namespace="/aquarium")

        # Randomly spawn a coin every few seconds
        if (random.random() < 0.01):
            # choose a fish to spawn from
            fish = random.choice([fish for fish in aquarium.objects.values() if isinstance(fish, Fish)])
            coin = Coin(aquarium, fish.x, fish.y)
            aquarium.objects[coin.label] = coin
            socketio.emit("update_thing", coin.summarize, namespace="/aquarium")
            
        # Every few seconds (SYNC_FREQUENCY), sync the current state of the aquarium to with all clients
        if (loop_start - last_sync).total_seconds() > SYNC_FREQUENCY:
            last_sync = loop_start
            socketio.emit("sync_everything", [thing.summarize for thing in aquarium.objects.values()], namespace="/aquarium")

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
