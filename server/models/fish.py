from server.models.aquarium import Fish
from server.helper import get_random_name
import random

class Clownfish(Fish):
    def __init__(self, aquarium, **kwargs):
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Clownfish")
        self.spritesheet_json = "assets/fish/clownfish.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.animation_prefix = "clownfish_"
        self.aspect_ratio = 1.3837209302
        self.width = 120
        self.max_speed = 100
        self.fish_name = f"{get_random_name(first_letter='C')} the Clownfish"
        self.coin_rate = 1/10

        self.food_preferences = [ 
            ("['Thing', 'Food', 'Pellet']", 0.1),
            ("['Thing', 'Food', 'Flake']", 0.5),
            ("['Thing', 'Fish']", 0.9),
        ]

        # Set properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _choose_state(self):
        closest_food, food_distance = self._find_food()
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        closest_tap, tap_distance = self._find_closest(class_hierarchy=["Thing", "Tap"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # Clownfish will prioritize feeding if there is food nearby
        if closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # Flee from larger predators
        elif (predator_distance < 200) and (predator_width > 1.5*self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If there are taps, then the fish will play if it likes the user (otherwise it will flee)
        elif (closest_tap is not None):
            if (self.relationships.get(closest_tap.username, 0) > 0.5):
                self.state = "playing"
                self.plaything = closest_tap
            else:
                self.state = "fleeing"
                self.predator = closest_tap
        # Otherwise, it will be idle
        else:
            self.state = "idle"

class Guppy(Fish):
    def __init__(self, aquarium, **kwargs):

        # Choose a random color for the guppy (if not specified)
        color = kwargs.get("color", None)
        if color is None:
            color = random.choice(["blue", "green", "orange", "pink", "red", "yellow"])
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Guppy")
        self.spritesheet_json = "assets/fish/guppy.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.animation_prefix = f"guppy_{color}_"
        self.spect_ratio = 1.4496644295
        self.width = 40
        self.max_speed = 80
        self.fish_name = f"{get_random_name(first_letter='G')} the Guppy"
        self.coin_rate = 1/40

        self.food_preferences = [ 
            ("['Thing', 'Food', 'Flake']", 0.1),
            ("['Thing', 'Food', 'Pellet']", 0.5),
            ("['Thing', 'Fish']", 1.0),
        ]

        # Set properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _choose_state(self):
        closest_food, food_distance = self._find_food()
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        closest_tap, tap_distance = self._find_closest(class_hierarchy=["Thing", "Tap"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # If the fish is being chased, it will prioritize fleeing
        if (predator_distance < 50) and (predator_width > self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If there is food nearby, it will prioritize feeding (thresholds set in self.food_preferences)
        elif closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If there are taps, then the fish will play if it likes the user (otherwise it will flee)
        elif (closest_tap is not None):
            if (self.relationships.get(closest_tap.username, 0) > 0.5):
                self.state = "playing"
                self.plaything = closest_tap
            else:
                self.state = "fleeing"
                self.predator = closest_tap
        # Otherwise, it will be idle
        else:
            self.state = "idle"

class Angelfish(Fish):
    def __init__(self, aquarium, **kwargs):

        # Choose a random color for the guppy (if not specified)
        color = kwargs.get("color", None)
        if color is None:
            color = random.choice(["green", "purple", "red", "turquoise", "yellow"])
            
        # Redefine properties from Fish
        super().__init__(aquarium)
        self.class_hierarchy.append("Angelfish")
        self.spritesheet_json = "assets/fish/angelfish.json"
        self.default_texture = None
        self.default_animation = "idle"
        self.animation_prefix = f"angelfish_{color}_"
        self.aspect_ratio = 1.2557377049
        self.width = 120
        self.max_speed = 100
        self.fish_name = f"{get_random_name(first_letter='A')} the Angelfish"
        self.coin_rate = 1/20 # Angelfish produce coins at a rate of 1 coin per 20 seconds (on average)

        self.food_preferences = [ 
            ("['Thing', 'Food', 'Pellet']", 0.1),
            ("['Thing', 'Food', 'Flake']", 0.5),
            ("['Thing', 'Fish']", 0.9),
        ]

        # Set properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _choose_state(self):
        closest_food, food_distance = self._find_food()
        closest_predator, predator_distance = self._find_closest(class_hierarchy=["Thing", "Fish"])
        closest_tap, tap_distance = self._find_closest(class_hierarchy=["Thing", "Tap"])
        predator_width = closest_predator.width if closest_predator is not None else 0
        # If the fish is being chased, it will prioritize fleeing
        if (predator_distance < 300) and (predator_width > self.width):
            self.state = "fleeing"
            self.predator = closest_predator
        # If there is food nearby, it will prioritize feeding (thresholds set in self.food_preferences)
        elif closest_food is not None:
            self.state = "feeding"
            self.food = closest_food
        # If there are taps, then the fish will play if it likes the user (otherwise it will flee)
        elif (closest_tap is not None):
            if (self.relationships.get(closest_tap.username, 0) > 0.2):
                self.state = "playing"
                self.plaything = closest_tap
            else:
                self.state = "fleeing"
                self.predator = closest_tap
        # Otherwise, it will be idle
        else:
            self.state = "idle"