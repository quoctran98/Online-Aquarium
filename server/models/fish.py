from server.models.game import Fish

class Guppy(Fish):
    def __init__(self, aquarium):

        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy = ["Thing", "Fish", "Guppy"]
        self.texture_file = "assets/fish/guppy.png"
        self.width = 20
        self.height = 10
        self.max_speed = 50
        # No new properties to broadcast

        # Set the guppy-specific properties
        self.fish_name = "unnamed_guppy"

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish", "Predator"])
        if self.hunger > 0.5 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If the fish is being chased, it will prioritize fleeing
        elif self.predator is not None and predator_distance < 100:
            self.state = "fleeing"
            self.predator = closest_predator
        # Otherwise, it will be idle
        else:
            self.state = "idle"

class Goldfish(Fish):
    def __init__(self, aquarium):
            
            # Redefine properties from Fish
            super().__init__(aquarium)
            self.class_hierarchy = ["Thing", "Fish", "Goldfish"]
            self.texture_file = "assets/fish/goldfish.png"
            self.width = 30
            self.height = 20
            self.max_speed = 30
            # No new properties to broadcast
    
            # Set the goldfish-specific properties
            self.fish_name = "unnamed_goldfish"

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish", "Predator"])
        if self.hunger > 0.5 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If the fish is being chased, it will prioritize fleeing
        elif self.predator is not None and predator_distance < 100:
            self.state = "fleeing"
            self.predator = closest_predator
        # Otherwise, it will be idle
        else:
            self.state = "idle"
