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

        # Set the goldfish-specific properties

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        if self.hunger > 0.5 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If the fish is being chased, it will prioritize fleeing
        elif predator_distance < 100:
            self.state = "fleeing"
            self.predator = closest_predator
        # Otherwise, it will be idle
        else:
            self.state = "idle"