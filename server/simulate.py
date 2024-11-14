from flask_socketio import emit
from server.helper import settings
from server.models.game import Fish, Aquarium, Coin, Food
from server.models.fish import Clownfish, Guppy
from server.models.user import User
from datetime import datetime, timezone
import time, random

# Move this to a config file later
SIMULATION_TICK = 0.05 # seconds per tick
SYNC_FREQUENCY = 1 # seconds per sync
BACKUP_FREQUENCY = 300 # seconds per backup

# This is the main game/simulation loop
# Either pass an existing aquarium or create a new one
def aquarium_simulation(socketio, command_queue, user_manager, aquarium):
    
    last_loop = datetime.now(timezone.utc)
    last_sync = datetime.now(timezone.utc)
    last_backup = datetime.now(timezone.utc)

    # Give it two free fish for debugging
    clownfish = Clownfish(aquarium)
    aquarium.objects[clownfish.label] = clownfish
    clownfish2 = Clownfish(aquarium)
    aquarium.objects[clownfish2.label] = clownfish2
    for _ in range(10):
        guppy = Guppy(aquarium)
        aquarium.objects[guppy.label] = guppy

    while True:

        # Start a timer and calculate the time since the last loop
        loop_start = datetime.now(timezone.utc)
        delta_time = loop_start - last_loop

        # Set a flag to indicate whether we should broadcast a sync (or update individual items)
        broadcast_sync = False
        broadcast_updates = []
      
        # Check if there are any commands in the queue
        while not command_queue.empty():
            command, data = command_queue.get()
            match command:
                case "add_fish":
                    fish_class = globals()[data["fish_class"]]
                    fish = fish_class(aquarium)
                    aquarium.fishes.append(fish)
                case "click":
                    if data["label"] in aquarium.objects:
                        item_clicked = aquarium.objects[data["label"]]
                        user_clicked = user_manager.get_by_username(data["username"])
                        user_clicked.money += item_clicked.value
                        user_clicked.save()
                        item_clicked.click(username=data["username"])
                        socketio.emit("update_user", user_clicked.summarize_public, namespace="/interactions")
                        broadcast_sync = True # Can't update only a single item that doesn't exist anymore...
                case "feed":
                    food = Food(aquarium, x=data["x"], y=data["y"])
                    aquarium.objects[food.label] = food
                    broadcast_updates.append(food.summarize)
                case "sync":
                    broadcast_sync = True
                case _:
                    Warning(f"Unknown command {command}")

        # Update all Things in the aquarium
        things_to_iterate = list(aquarium.objects.values()) # Prevent the dict from changing size during iteration
        for thing in things_to_iterate:
            thing.update(delta_time)
            changed = thing.updated_this_loop
            if changed:
                broadcast_updates.append(thing.summarize)

        # Randomly spawn a coin every few seconds
        if (random.random() < 0.001):
            # choose a fish to spawn from
            fish = random.choice([fish for fish in aquarium.objects.values() if isinstance(fish, Fish)])
            coin = Coin(aquarium, fish.x, fish.y)
            aquarium.objects[coin.label] = coin
            broadcast_updates.append(coin.summarize)
            
        # Every few seconds (SYNC_FREQUENCY), sync the current state of the aquarium to with all clients
        # Or if a broadcast_sync flag is set
        if ((loop_start - last_sync).total_seconds() > SYNC_FREQUENCY) or broadcast_sync:
            last_sync = loop_start
            socketio.emit("sync_everything", [thing.summarize for thing in aquarium.objects.values()], namespace="/aquarium")
        
        # Broadcast individual updates for Things that require it
        # No need to do it if we're already syncing everything
        else:
            for summarized_update in broadcast_updates:
                socketio.emit("update_thing", summarized_update, namespace="/aquarium")

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
