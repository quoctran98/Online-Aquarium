from server.helper import settings, fish_stats, aquarium_stats
import random, math, uuid

class Fish():
    def __init__(self, type: str, aquarium):
        self.type: str = type
        self.aquarium = aquarium
        self.id = uuid.uuid4()

        if type not in fish_stats:
            raise ValueError(f"Fish type {type} not found in fish_stats")
        self.__dict__.update(fish_stats[type])

        # Available states: idle, eating, 
        self.state = "idle"

        # Relative position in the aquarium; (0,0) is the top left corner
        self.facing = "right"
        self.direction = random.uniform(0, 2 * math.pi)
        self.position = {
            "x": aquarium.width / 2,
            "y": aquarium.height / 2
        }
    
    def idle_swim(self, delta_time):
        if random.random() < 0.01:
            self.direction = random.uniform(0, 2 * math.pi)
        if self.direction < math.pi:
            self.facing = "right"
        else:
            self.facing = "left"
        new_x = self.speed * math.cos(self.direction) * delta_time.total_seconds() + self.position["x"]
        new_y = self.speed * math.sin(self.direction) * delta_time.total_seconds() + self.position["y"]
        if new_x < 0:
            new_x = 0
            self.direction = math.pi - self.direction
        if new_x > self.aquarium.width:
            new_x = self.aquarium.width
            self.direction = -math.pi
        if new_y < 0:
            new_y = 0
            self.direction = -self.direction
        if new_y > self.aquarium.height:
            new_y = self.aquarium.height
            self.direction = math.pi
        self.position = {
            "x": new_x,
            "y": new_y
        }

    def update(self, delta_time):
        if self.state == "idle":
            self.idle_swim(delta_time)
        elif self.state == "eating":
            pass
        else:
            Warning(f"Unknown fish state {self.state}")

    @property
    def serialize(self):
        return({
            "id": str(self.id),
            "type": self.type,
            "length": self.length,
            "position": self.position,
            "facing": self.facing
        })
        
class Aquarium():
    def __init__(self, type: str):
        self.type = type

        if type not in aquarium_stats:
            raise ValueError(f"Aquarium type {type} not found in aquarium_stats")
        self.__dict__.update(aquarium_stats[type])

        self.fishes = []

