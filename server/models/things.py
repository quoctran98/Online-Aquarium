from server.models.game import Thing
import datetime, random, math

class Food(Thing):
    def __init__(self, aquarium, x=None, y=None):

        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy.append("Food")
        self.spritesheet_json = "assets/things.json"
        self.default_texture = "pellet.png"
        self.default_animation = None
        self.width = 10
        self.height = 10
        self.properties_to_broadcast.extend([
            "nutrition"
        ])

        # Set the food-specific properties
        self.nutrition = 0.1 # 0 to 1
        self.lifetime = 60 # Seconds

        # Make the food fall straight down
        self.x = x
        self.y = y
        self.destination_x = self.x
        self.destination_y = aquarium.height - self.height
        self.speed = 20 # Pixels per second

    def update(self, delta_time):
        self.updated_this_loop = False
        self._move_toward_destination(delta_time)
        self._calculate_lifetime()

class Coin(Thing):
    def __init__(self, aquarium, x=None, y=None):

        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy.append("Coin")
        self.spritesheet_json = "assets/things.json"
        self.default_texture = "coin.png"
        self.default_animation = None
        self.width = 20
        self.height = 20
        self.properties_to_broadcast.extend([
            "value"
        ])

        # Set the coin-specific properties
        self.value = 0.01
        self.lifetime = 60 # Seconds

        # Make the coin fall straight down
        self.x = x
        self.y = y
        self.destination_x = x
        self.destination_y = aquarium.height - self.height
        self.speed = 100 # Pixels per second

    def update(self, delta_time):
        self.updated_this_loop = False
        self._move_toward_destination(delta_time)
        self._calculate_lifetime()

    def click(self, user):
        user.money = round(user.money + self.value, 2)
        user.save()
        self.remove()

class TreasureChest(Thing):
    def __init__(self, aquarium, x=None, y=None):

        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy.append("TreasureChest")
        self.spritesheet_json = "assets/things.json"
        self.default_texture = "treasure_chest_closed.png"
        self.default_animation = None
        self.width = 348.50/2
        self.height = 256/2
        self.properties_to_broadcast.extend([
            "state", "value", "closed_texture", "empty_texture", "full_texture"
        ])

        # Set the chest-specific properties
        self.closed_texture = "treasure_chest_closed.png"
        self.empty_texture = "treasure_chest_empty.png"
        self.full_texture = "treasure_chest_full.png"
        self.state = "closed" # "closed", "empty", "full"
        self.value_range = (0.05, 0.25) # Random value when the chest is full
        self.value = round(random.uniform(*self.value_range), 2) # Set an initial value
        self.duty_cycle = (4, 6) # Seconds closed, seconds open
        self.full_probability = 0.1 # Probability of the chest being full when it opens
        self.last_change = datetime.datetime.now().timestamp() * 1000 # ms since epoch (last state change)
        self.bubble_freqeuency = 1.5 # Seconds between bubbles
        self.last_bubble = datetime.datetime.now().timestamp() * 1000 # ms since epoch (last bubble)

        # Set the chest's position and make it not move 
        # # (also we won't call _move_toward_destination in update)
        self.x = x
        self.y = y
        self.destination_x = x
        self.destination_y = y
        self.speed = 0

    def _calculate_state(self):
        time_since_change = datetime.datetime.now().timestamp() * 1000 - self.last_change # ms
        if (self.state == "closed"):
            if (time_since_change > (self.duty_cycle[0] * 1000)):
                # Open the chest and make it full or empty and reset the timer
                self.state = "full" if random.random() < self.full_probability else "empty"
                self.value = round(random.uniform(*self.value_range), 2) # No need for an if statement here (won't be clikable if empty)
                self.last_change = datetime.datetime.now().timestamp() * 1000
                self.updated_this_loop = True
        elif (self.state in ["empty", "full"]):
            if (time_since_change > (self.duty_cycle[1] * 1000)):
                # Close the chest and reset the timer
                self.state = "closed"
                self.last_change = datetime.datetime.now().timestamp() * 1000
                self.updated_this_loop = True
        else:
            raise ValueError(f"Invalid state: {self.state}")

    def _emit_bubbles(self):
        # Emit bubbles when there is no treasure in the chest
        time_since_bubble = datetime.datetime.now().timestamp() * 1000 - self.last_bubble # ms
        if (self.state == "empty") and (time_since_bubble > (self.bubble_freqeuency * 1000)):
            # Don't forget pivot is center of the object (when rendering!)
            bubble_x = random.randrange(math.ceil(self.x - self.width/3), math.floor(self.x + self.width/3))
            bubble_y = self.y - (random.random() * self.height/3) # Looks good, I think :)
            bubble = Bubble(self.aquarium, bubble_x, bubble_y)
            self.aquarium.add_object(bubble)
            self.last_bubble = datetime.datetime.now().timestamp() * 1000

    def update(self, delta_time):
        self.updated_this_loop = False
        self._calculate_state()
        self._emit_bubbles()

    def click(self, user):
        # If it's full, give the user the money and set the state to empty
        if self.state == "full":
            self.state = "empty"
            self.updated_this_loop = True
            user.money = round(user.money + self.value, 2)
            user.save()

class Bubble(Thing):
    def __init__(self, aquarium, x, y):

        # Redefine properties from Thing
        super().__init__(aquarium)
        self.class_hierarchy.append("Bubble")
        self.spritesheet_json = "assets/things.json"
        self.default_texture = "bubble.png"
        self.default_animation = None
        self.width = random.randint(20, 40)
        self.height = self.width
        # self.properties_to_broadcast.extend([])
        # No bubble-specific properties!

        # Make the bubble rise
        self.x = x 
        self.y = y
        self.destination_x = self.x
        self.destination_y = 0 + self.height + random.randint(10, 50) # 10 to 50 pixels below the surface
        self.speed = self.width / 2 # Pixels per second (bigger bubbles rise faster)

    def update(self, delta_time):
        self.updated_this_loop = False
        self._move_toward_destination(delta_time)
        if (self.y <= self.destination_y):
            self.remove() # Pop the bubble when it reaches the top (no animation for now)
