from server.helper import settings, save_to_s3
import random, math, uuid, datetime, os, pickle

class Aquarium():
    def __init__(self, command_queue, width=960, height=540):
        self.width = width
        self.height = height
        self.objects = {}
        self.command_queue = command_queue

        # Keep track of updated objects for broadcasting
        self.broadcast_updates = [] # Moved from the simluate.py loop :)
        
        # We don't usually need to broadcast the Aquarium 
        self.properties_to_broadcast = [
            "width", "height"
        ]

    def create_object(self, class_name, kwargs={}, properties={}):
        # Use this when creating new objects where the class isn't imported yet
        # Do this through the command queue and maintain the simulate.py as the main namespace?
        self.command_queue.put(("create", {
            "object_name": class_name, 
            "object_kwargs": kwargs, 
            "object_properties" : properties
        }))

    def add_object(self, object):
        self.objects[object.label] = object
        self.broadcast_updates.append(object.summarize)
        # This method more easily allows us to add add objects from children.

    def remove_object(self, object):
        self.objects.pop(object.label)
        # We should think about how to broadcast this change...
        object_summarize = object.summarize
        object_summarize["remove"] = True
        self.broadcast_updates.append(object_summarize)

    def update(self, delta_time):
        # Nothing to do here yet...
        pass

    @property
    def summarize(self):
        return_dict = {
            "update_time": datetime.datetime.now().timestamp() * 1000,
            "objects": [label for label in self.objects.keys()]
        }
        for prop in self.properties_to_broadcast:
            return_dict[prop] = getattr(self, prop)
        return(return_dict)

    def save(self, save_dir=settings.S3_AQUARIUM_SAVE_DIR):
        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_aquarium.pkl"
        # WE HAVE TO DETACH THE COMMAND QUEUE BEFORE PICKLING!!!
        command_queue = self.command_queue
        self.command_queue = None
        pickle_obj = pickle.dumps(self)
        save_to_s3(pickle_obj, filename, save_dir)
        # Maybe not the best way, but let's also save a "latest" version!!
        save_to_s3(pickle_obj, "latest.pkl", save_dir)
        # REATTACH THE COMMAND QUEUE
        self.command_queue = command_queue

class Thing():
    def __init__(self, aquarium):
        self.aquarium = aquarium
        self.label = str(uuid.uuid4())

        # Size properties
        self.aspect_ratio = None # aspect_ratio = width / height
        self.width = 0
        self._height = 0

        # Position and movement properties
        self.x = 0
        self.y = 0
        self.speed = 0
        self.destination_x = 0
        self.destination_y = 0

        # Lifetime properties and housekeeping
        self.time_created = datetime.datetime.now().timestamp() * 1000
        self.lifetime = None # Seconds, None for infinite

        # Texture/animation properties
        self.spritesheet_json = None
        self.default_texture = None
        self.default_animation = None
        self.animation_prefix = "" # For spritesheets with multiple animations

        # Houskeeping properties
        self.class_hierarchy = ["Thing"]
        self.updated_this_loop = False
        self.properties_to_broadcast = [
            "label", "class_hierarchy", "x", "y", "speed", "destination_x", "destination_y", "aspect_ratio",
            "width", "height", "time_created", "spritesheet_json", "default_texture", "default_animation", "animation_prefix"
        ]

    @property
    def height(self):
        if self.aspect_ratio is None:
            return(self._height)
        else:
            return(self.width / self.aspect_ratio)

    def update(self, delta_time):
        # Placeholder for child classes to override
        # Will be called by the simulation loop. Return a list of changes to broadcast to the front-end
        self._move_toward_destination(delta_time)

    def remove(self):
        self.aquarium.remove_object(self)

    def click(self):
        # Placeholder for child classes to override
        # Will be called by in the command queue when a user clicks on the object
        # This will occur BEFORE the update loop (and the update loop will call update() again)
        pass

    def _new_object_destination(self, object, speed=None):
        # Set a new object as the destination
        self.destination_x = object.x
        self.destination_y = object.y
        self.speed = speed if speed is not None else self.max_speed
        self.updated_this_loop = True

    def _move_toward_destination(self, delta_time):
        # Could be optimized by only calculating the direction once (but that's another property to keep track of)
        direction = math.atan2(self.destination_y - self.y, self.destination_x - self.x)
        new_x = self.speed * math.cos(direction) * delta_time.total_seconds() + self.x
        new_y = self.speed * math.sin(direction) * delta_time.total_seconds() + self.y
        new_x = max(0, min(new_x, self.aquarium.width))
        new_y = max(0, min(new_y, self.aquarium.height))
        # Make sure we haven't overshot the destination 
        if (self.destination_x - self.x) * (self.destination_x - new_x) < 0:
            new_x = self.destination_x
        if (self.destination_y - self.y) * (self.destination_y - new_y) < 0:
            new_y = self.destination_y
        self.x = new_x
        self.y = new_y

    def _calculate_lifetime(self):
        if self.lifetime is None:
            return
        if (datetime.datetime.now().timestamp() * 1000 - self.time_created) > self.lifetime * 1000:
            self.remove()

    def _is_colliding(self, other):
        # Check if the bounding boxes of two objects are overlapping
        if (self.x < other.x + other.width and self.x + self.width > other.x and
            self.y < other.y + other.height and self.y + self.height > other.y):
            return(True)
        else:
            return(False)
        
    def _find_closest(self, class_hierarchy=["Thing"]) -> tuple:
        # Find the closest object of a certain class
        closest = None
        closest_distance = float("inf")
        for obj in self.aquarium.objects.values():
            if obj.label == self.label:
                continue # Skip self
            if not all([c in obj.class_hierarchy for c in class_hierarchy]):
                # Skip objects that don't match the class hierarchy
                # This doesn't respect order of the list, but it shouldn't matter
                continue 
            distance = math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)
            if distance < closest_distance:
                closest = obj
                closest_distance = distance
        return(closest, closest_distance)

    @property
    def summarize(self):
        return_dict = {
            "update_time": datetime.datetime.now().timestamp() * 1000
        }
        for prop in self.properties_to_broadcast:
            return_dict[prop] = getattr(self, prop)
        return(return_dict)

class Fish(Thing):
    def __init__(self, aquarium):
        
        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy.append("Fish")
        self.spritesheet_json = "assets/things.json"
        self.default_texture = "fish.png"
        self.default_animation = None
        self.aspect_ratio = 1
        self.width = 100 # Pixels (also a proxy for size!)
        self.properties_to_broadcast.extend([
            "fish_name", "state", "health", "happiness", "hunger" 
        ])

        # Set the fish-specific properties
        self.fish_name = "unnamed_fish"
        self.state = "idle" # idle, feeding, fleeing, playing

        # Health properties (check `game_classes.md` for more info)
        self.health = 1.0
        self.happiness_health_rate = 1/14400 
        self.happiness = 0.5 # 0 to 1

        # Hunger properties
        self.hunger = 0 # 0 to 1, 1 is very hungry
        self.hunger_rate = 1/1440000 # Hunger per second per speed per width (4 hours at speed=100 and width=100)
        self.starve_rate = 1/7200 # Health per second per (0.5-hunger) (2 hours at hunger=1)

        self.max_speed = 100 # Pixels per second

        # Keep a running tally of how much a fish likes a user
        self.relationships = {} # {user_id: relationship_score (0 to 1)}

        # References for when the fish is in a certain state
        self.food = None # Food or Fish object
        self.predator = None # Fish object
        self.plaything = None # Fish or Tap or other object

    def _die(self):
        self.aquarium.create_object("Skeleton", kwargs={"fish": self}, properties={})
        self.remove()

    def _calculate_health(self, delta_time):
        self.health += ((0.5 - self.hunger) * self.starve_rate - (0.5 - self.happiness) * self.happiness_health_rate) * delta_time.total_seconds()
        if (self.health <= 0):
            self._die()
        self.health = max(0, min(1, self.health))

    def _calculate_happiness(self, delta_time):
        # Placeholder for child classes to override with fish-specific behavior
        pass

    def _calculate_hunger(self, delta_time):
        self.hunger += self.hunger_rate * self.speed * delta_time.total_seconds()
        self.hunger = max(0, min(self.hunger, 1))

    def _choose_state(self):
        # Placeholder for child classes to override with fish-specific behavior
        self.state = "idle"

    def _playing(self, delta_time):
        if (self.plaything is None) or (self.plaything not in self.aquarium.objects.values()):
            self.state = "idle"
            self.plaything = None
        else:
            self._new_object_destination(self.plaything, speed=self.max_speed)
            self._move_toward_destination(delta_time)
    
    def _idle(self, delta_time):
        # Default idle behavior is to move around randomly
        has_new_destination = False
        if math.sqrt((self.destination_x - self.x)**2 + (self.destination_y - self.y)**2) < 10:
            # If the fish is within 10 pixels of its destination, choose a new one
            self.destination_x = random.uniform(0 + self.width, self.aquarium.width - self.width)
            self.destination_y = random.uniform(0 + self.height, self.aquarium.height - self.height)
            self.speed = random.uniform(self.max_speed/4, self.max_speed/2)
            self.updated_this_loop = True
        # Move the fish towards its destination
        self._move_toward_destination(delta_time)

    def _feeding(self, delta_time):
        # Always set updated_this_loop to True for smoother frontend updates
        self.updated_this_loop = True
        # If the food is gone, return to idle state
        if (self.food is None) or (self.food not in self.aquarium.objects.values()):
            self.state = "idle"
            self.food = None
            self.updated_this_loop = True
        if self._is_colliding(self.food): 
            self.food.remove()
            self.hunger = max(0, min(1, self.hunger - self.food.nutrition))
            self.state = "idle"
            self.food = None
        # Otherwise, move towards the food
        else:
            self._new_object_destination(self.food, speed=self.max_speed)
            self._move_toward_destination(delta_time)

    def _fleeing(self, delta_time):
        # Always set updated_this_loop to True for smoother frontend updates
        self.updated_this_loop = True
        # If the predator is gone, return to idle state
        if (self.predator is None) or (self.predator not in self.aquarium.objects.values()):
            self.state = "idle"
            self.predator = None
        # Otherwise, move away from the predator
        else:
            angle_away = math.atan2(self.y - self.predator.y, self.x - self.predator.x)
            self.destination_x = self.x + 100 * math.cos(angle_away)
            self.destination_y = self.y + 100 * math.sin(angle_away)
            self.destination_x = max(0 + self.width, min(self.destination_x, self.aquarium.width - self.width))
            self.destination_y = max(0 + self.height, min(self.destination_y, self.aquarium.height - self.height)) 
            self.speed = self.max_speed
            self._move_toward_destination(delta_time)

    def update(self, delta_time) -> bool:
        # Housekeeping stuff)
        self.updated_this_loop = False
        self._calculate_health(delta_time)
        self._calculate_happiness(delta_time)
        self._calculate_hunger(delta_time)
        self._choose_state()
        # State-specific behavior
        if self.state == "idle":
            self._idle(delta_time)
        elif self.state == "feeding":
            self._feeding(delta_time)
        elif self.state == "fleeing":
            self._fleeing(delta_time)
        elif self.state == "playing":
            self._playing(delta_time)
        else:
            try:
                exec(f"self._{self.state}(delta_time)")
            except:
                Warning(f"Unknown fish state {self.state}")
        return(self.updated_this_loop)
