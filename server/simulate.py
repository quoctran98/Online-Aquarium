from flask_socketio import emit
from server.helper import settings
from server.models.aquarium import Fish, Aquarium
from server.models.fish import Clownfish, Guppy
from server.models.things import Coin, Food, TreasureChest, Tap
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

    while True:

        # Start a timer and calculate the time since the last loop
        loop_start = datetime.now(timezone.utc)
        delta_time = loop_start - last_loop

        # Set a flag to indicate whether we should broadcast a sync (or update individual items)
        broadcast_sync = False
        # broadcast_updates = [] -> moved to a property of the aquarium
        # Reset aquarium.broadcast_updates
        aquarium.broadcast_updates = []
      
        # Check if there are any commands in the queue
        while not command_queue.empty():
            command, data = command_queue.get()
            match command:
                
                case "add":
                    # Add a new item to the aquarium (when something is purchased)
                    object_name = data["object_name"]
                    object_kwargs = data["object_kwargs"]
                    object_properties = data["object_properties"]
                    new_object = eval(f"{object_name}(aquarium, **object_kwargs)")
                    for key, value in object_properties.items():
                        setattr(new_object, key, value)
                    aquarium.add_object(new_object) # This will also add it to aquarium.broadcast_updates

                case "tap": 
                    #  Users are ensured to exist before data is sent to the queue! No need to check here :)
                    user = User.get_by_username(data["username"])
                    aquarium.add_object(Tap(aquarium, data["x"], data["y"], user.username))

                case "pickup" | "click": # No functional difference between the two
                    # How do we deal with multiple users interacting with the same object?
                    if (data["thing_label"] in aquarium.objects):
                        user = user_manager.get_by_username(data["username"])
                        aquarium.objects[data["thing_label"]].click(user)
                        socketio.emit("update_user", user.summarize_public, namespace="/interactions")
                        broadcast_sync = True # Can't broadcast an update for an item that no longer exists

                case "use":
                    match data["tool"]:
                        case "fish_flakes":
                            flakes = Food(aquarium, data["x"], data["y"])
                            aquarium.add_object(flakes)

                case "sync":
                    broadcast_sync = True

                case _:
                    Warning(f"Unknown command {command}")

        # Update the actual aquarium itself!
        aquarium.update(delta_time)

        # Update all Things in the aquarium
        things_to_iterate = list(aquarium.objects.values()) # Prevent the dict from changing size during iteration
        for thing in things_to_iterate:
            thing.update(delta_time)
            changed = thing.updated_this_loop
            if changed:
                aquarium.broadcast_updates.append(thing.summarize)

        # Randomly spawn a coin every few seconds
        if (random.random() < 0.001):
            # choose a fish to spawn from
            fish = random.choice([fish for fish in aquarium.objects.values() if isinstance(fish, Fish)])
            coin = Coin(aquarium, fish.x, fish.y)
            aquarium.add_object(coin)
            
        # Every few seconds (SYNC_FREQUENCY), sync the current state of the aquarium to with all clients
        # Or if a broadcast_sync flag is set
        if ((loop_start - last_sync).total_seconds() > SYNC_FREQUENCY) or broadcast_sync:
            last_sync = loop_start
            socketio.emit("sync_everything", [thing.summarize for thing in aquarium.objects.values()], namespace="/aquarium")
        
        # Broadcast individual updates for Things that require it
        # No need to do it if we're already syncing everything
        else:
            for summarized_update in aquarium.broadcast_updates:
                socketio.emit("update_thing", summarized_update, namespace="/aquarium")

        # Every few minutes (BACKUP_FREQUENCY), save the current state of the aquarium
        if (loop_start - last_backup).total_seconds() > BACKUP_FREQUENCY:
            last_backup = loop_start
            aquarium.save()
            print(f"Backup saved at {last_backup}")

        # Calculate the time it took to run the loop and wait for the next tick
        loop_end = datetime.now(timezone.utc)
        last_loop = loop_end
        loop_time = (loop_end - loop_start).total_seconds()
        if loop_time > SIMULATION_TICK:
            Warning(f"Loop took {loop_time} seconds, which is longer than the tick time of {SIMULATION_TICK} seconds")
        time.sleep(max(0, SIMULATION_TICK - loop_time))
