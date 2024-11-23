from server.models.aquarium import Fish

class Clownfish(Fish):
    def __init__(self, aquarium, **kwargs):
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Clownfish")
        self.spritesheet_json = "assets/fish/clownfish.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.aspect_ratio = 1.3837209302
        self.width = 120
        self.max_speed = 100
        self.fish_name = "nemo"
        # No new properties to broadcast

        self.starve = False

        # Set properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        closest_tap, tap_distance = self._find_closest(class_hierarchy=["Thing", "Tap"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # Clownfish will priortize feeding
        if self.hunger > 0.5 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # Flee from larger predators
        elif (predator_distance < 200) and (predator_width > 1.5*self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If there are taps, then the fish will play
        elif closest_tap is not None:
            self.state = "playing"
            self.plaything = closest_tap
        # Otherwise, it will be idle
        else:
            self.state = "idle"

class Guppy(Fish):
    def __init__(self, aquarium, **kwargs):
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Guppy")
        self.spritesheet_json = "assets/fish/guppy.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.spect_ratio = 1.4496644295
        self.width = 72
        self.max_speed = 80
        self.fish_name = "fish"
        # No new properties to broadcast

        self.starve = False

        # Set properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        closest_tap, tap_distance = self._find_closest(class_hierarchy=["Thing", "Tap"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # If the fish is being chased, it will prioritize fleeing
        if (predator_distance < 300) and (predator_width > self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If the fish is hungry and there is food nearby, it will prioritize feeding
        elif self.hunger > 0.2 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If there are taps, then the fish will play
        elif closest_tap is not None:
            self.state = "playing"
            self.plaything = closest_tap
        # Otherwise, it will be idle
        else:
            self.state = "idle"

class Angelfish(Fish):
    def __init__(self, aquarium, **kwargs):
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Angelfish")
        self.spritesheet_json = "assets/fish/green_angelfish.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.aspect_ratio = 1.2557377049
        self.width = 120
        self.max_speed = 100
        self.fish_name = "julian"
        # No new properties to broadcast

        self.starve = False

        # Set properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _choose_state(self):
        closest_food, food_distance = self._find_closest(class_hierarchy=["Thing", "Food"])
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        closest_tap, tap_distance = self._find_closest(class_hierarchy=["Thing", "Tap"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # If the fish is being chased, it will prioritize fleeing
        if (predator_distance < 300) and (predator_width > self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If the fish is hungry and there is food nearby, it will prioritize feeding
        elif self.hunger > 0.2 and closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If there are taps, then the fish will play
        elif closest_tap is not None:
            self.state = "playing"
            self.plaything = closest_tap
        # Otherwise, it will be idle
        else:
            self.state = "idle"