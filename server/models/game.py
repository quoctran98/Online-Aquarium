from server.helper import settings, aquarium_types
import random, math, uuid, datetime, os, pickle

class Aquarium():
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.objects = {}
        self.properties_to_broadcast = [
            "width", "height"
        ]

    def summarize(self):
        return_dict = {
            "update_time": datetime.datetime.now().timestamp() * 1000,
            "objects": [label for label in self.objects.keys()]
        }
        for prop in self.properties_to_broadcast:
            return_dict[prop] = getattr(self, prop)
        return(return_dict)

    def save(self, save_dir):
        fname = os.path.join(save_dir, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_aquarium.pkl")
        with open(fname, "wb") as f:
            pickle.dump(self, f)

class Thing():
    def __init__(self, aquarium):
        self.aquarium = aquarium
        self.label = str(uuid.uuid4())
        self.class_hierarchy = ["Thing"]
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.speed = 0
        self.destination_x = 0
        self.destination_y = 0
        self.time_created = datetime.datetime.now().timestamp() * 1000
        self.texture_file = "assets/placeholders/nothing.png"
        self.properties_to_broadcast = [
            "label", "class_hierarchy", "x", "y", "speed", "destination_x", "destination_y",
            "width", "height", "time_created", "texture_file"
        ]

    def update(self, delta_time):
        # Placeholder for child classes to override
        # Will be called by the simulation loop. Return a list of changes to broadcast to the front-end
        self._move_toward_destination(delta_time)

    def remove(self):
        self.aquarium.objects.pop(self.label)

    def _move_toward_destination(self, delta_time):
        # Could be optimized by only calculating the direction once (but that's another property to keep track of)
        direction = math.atan2(self.destination_y - self.y, self.destination_x - self.x)
        new_x = self.speed * math.cos(direction) * delta_time.total_seconds() + self.x
        new_y = self.speed * math.sin(direction) * delta_time.total_seconds() + self.y
        new_x = max(0, min(new_x, self.aquarium.width))
        new_y = max(0, min(new_y, self.aquarium.height))
        self.x = new_x
        self.y = new_y

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
        self.class_hierarchy = ["Thing", "Fish"]
        self.texture_file = "assets/placeholders/fish.png"
        self.width = 20
        self.height = 20
        self.properties_to_broadcast.extend([
            "state", "hunger",
        ])

        # Set the fish-specific properties
        self.fish_name = "unnamed_fish"
        self.state = "idle" # idle, feeding, fleeing,
        self.hunger = 0.0 # 0 to 1
        self.hunger_decay_rate = 0.01 # Per second
        self.max_speed = 0 # Pixels per second

        # References for when the fish is in a certain state
        self.food = None # Food or Fish object
        self.predator = None # Fish object

    def _calculate_hunger(self, delta_time):
        self.hunger -= self.hunger_decay_rate * delta_time.total_seconds()
        self.hunger = max(0, min(self.hunger, 1))

    def _choose_state(self):
        # Placeholder for child classes to override with fish-specific behavior
        self.state = "idle"
    
    def __idle(self, delta_time) -> bool:
        # Default idle behavior is to move around randomly
        has_new_destination = False
        if math.sqrt((self.destination_x - self.x)**2 + (self.destination_y - self.y)**2) < 10:
            # If the fish is within 10 pixels of its destination, choose a new one
            self.destination_x = random.uniform(0, self.aquarium.width)
            self.destination_y = random.uniform(0, self.aquarium.height)
            self.speed = random.uniform(self.max_speed/4, self.max_speed/2)
            has_new_destination = True
        # Move the fish towards its destination
        self._move_toward_destination(delta_time)
        return(has_new_destination)

    def __feeding(self, delta_time) -> bool:
        # If the food is gone, return to idle state
        if self.food is None or self.food not in self.aquarium.objects:
            self.state = "idle"
            self.food = None
            return(True)
        # If the fish has reached the food, eat it
        if self._is_colliding(self.food): 
            self.food.remove()
            self.hunger = min(0, max(1, self.hunger + self.food.nutrition))
            self.state = "idle"
            self.food = None
            return(True)
        # Otherwise, move towards the food
        else:
            self.destination_x = self.food.x
            self.destination_y = self.food.y
            self.speed = self.max_speed
            self._move_toward_destination(delta_time)
            return(False) # No state change, still feeding

    def __fleeing(self, delta_time) -> bool:
        # If the predator is gone, return to idle state
        if self.predator is None or self.predator not in self.aquarium.objects:
            self.state = "idle"
            self.predator = None
            return(True)
        # Otherwise, move away from the predator
        else:
            angle_away = math.atan2(self.y - self.predator.y, self.x - self.predator.x)
            self.destination_x = self.x + 100 * math.cos(angle_away)
            self.destination_y = self.y + 100 * math.sin(angle_away)
            self.destination_x = max(0, min(self.destination_x, self.aquarium.width))
            self.destination_y = max(0, min(self.destination_y, self.aquarium.height))
            self.speed = self.max_speed
            self._move_toward_destination(delta_time)
            return(False) # No state change, still fleeing

    def update(self, delta_time) -> bool:
        # Housekeeping stuff)
        self._calculate_hunger(delta_time)
        self._choose_state()
        # State-specific behavior
        if self.state == "idle":
            return(self.__idle(delta_time))
        elif self.state == "feeding":
            return(self.__feeding(delta_time))
        elif self.state == "fleeing":
            return(self.__fleeing(delta_time))
        else:
            Warning(f"Unknown fish state {self.state}")
            return(False)
        
class Food(Thing):
    def __init__(self, aquarium, x=None, y=None):

        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy = ["Thing", "Food"]
        self.texture_file = "assets/pellet.png"
        self.width = 10
        self.height = 10
        self.properties_to_broadcast.extend([
            "nutrition"
        ])

        # Set the food-specific properties
        self.nutrition = 0.1

        # Make the food fall straight down
        self.x = x
        self.y = y
        self.destination_x = self.x
        self.destination_y = aquarium.height
        self.speed = 50 # Pixels per second

class Coin(Thing):
    def __init__(self, aquarium, x=None, y=None):

        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy = ["Thing", "Coin"]
        self.texture_file = "assets/coin.png"
        self.width = 20
        self.height = 20
        self.properties_to_broadcast.extend([
            "value", "lifetime"
        ])

        # Set the coin-specific properties
        self.value = 1
        self.lifetime = 60 # Seconds

        # Make the coin fall straight down
        self.x = x
        self.y = y
        self.destination_x = x
        self.destination_y = aquarium.height
        self.speed = 100 # Pixels per second

    def update(self, delta_time):
        # Move the coin towards its destination
        self._move_toward_destination(delta_time)
        self.lifetime -= delta_time.total_seconds()
        if self.lifetime < 0:
            self.remove()
            return(True)
        else:
            return(False)
