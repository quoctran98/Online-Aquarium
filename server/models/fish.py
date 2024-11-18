from server.models.game import Fish

class Clownfish(Fish):
    def __init__(self, aquarium):
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Clownfish")
        self.spritesheet_json = "assets/fish/clownfish.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.width = 120
        self.height = 86.7 # Maintain aspect ratio of the sprite
        self.max_speed = 100
        self.fish_name = "nemo"
        # No new properties to broadcast

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # Clownfish will priortize feeding
        if self.hunger > 0.5 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # Flee from larger predators
        elif (predator_distance < 200) and (predator_width > 1.5*self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # Otherwise, it will be idle
        else:
            self.state = "idle"

class Guppy(Fish):
    def __init__(self, aquarium):
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Guppy")
        self.spritesheet_json = "assets/fish/guppy.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.width = 72
        self.height = 49.7 # Maintain aspect ratio of the sprite
        self.max_speed = 80
        self.fish_name = "fish"
        # No new properties to broadcast

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # If the fish is being chased, it will prioritize fleeing
        if (predator_distance < 300) and (predator_width > self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If the fish is hungry and there is food nearby, it will prioritize feeding
        elif self.hunger > 0.2 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # Otherwise, it will be idle
        else:
            self.state = "idle"