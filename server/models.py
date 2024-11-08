from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from server.helper import settings, mongo_users_collection, fish_types, aquarium_types
import random, math, uuid, datetime, os, pickle, time

class User(UserMixin):
    def __init__(self, username, password, user_id=None, _id=None):
        # We might need to implement user_id this way for Flask-Login? Yeah!
        self.user_id = uuid.uuid4().hex if user_id is None else str(user_id)
        self.mongo_id = None if _id is None else str(_id) # MongoDB _id
        self.username = username
        self.hashed_password = password

    # Methods required by Flask-Login
    def is_authenticated(self):
        return(True)
    def is_active(self):
        return(True)
    def is_anonymous(self):
        return(False)
    def get_id(self):
        return(self.user_id)

    def check_password(self, input_password):
        return(check_password_hash(self.hashed_password, input_password))

    @classmethod
    def get_by_username(cls, username):
        data = mongo_users_collection.find_one({"username": username})
        if data:
            return(cls(**data))
        return(None)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        data = mongo_users_collection.find_one({"user_id": user_id})
        if data:
            return(cls(**data))
        return(None)
    
    @classmethod
    def signup(cls, username, unhashed_password):
        user = cls.get_by_username(username)
        if user: # User already exists
            return(False)
        else: # Create a new user
            hashed_password = generate_password_hash(unhashed_password)
            mongo_users_collection.insert_one({
                "username": username, 
                "password": hashed_password,
                "user_id": uuid.uuid4().hex})
            return(True)
        
    @classmethod
    def guest_user(cls):
        # Return a User object for a guest user
        guest_name = "guest_" + uuid.uuid4().hex[:8]
        return(cls(
            username=guest_name,
            password=None, # Hopefully this doesn't break anything
        ))
    
    @property
    def serialize_public(self):
        return({
            "username": self.username,
            "user_id": self.user_id
        })

class Fish():
    def __init__(self, type, aquarium):
        self.type = type
        self.name = "fish"
        self.aquarium = aquarium
        self.id = uuid.uuid4()

        if type not in fish_types:
            raise ValueError(f"Fish type {type} not found in fish_types")
        self.__dict__.update(fish_types[type])
        # Includes: length, max_speed

        # Randomize the fish's starting position for now
        self.x = random.uniform(0, aquarium.width)
        self.y = random.uniform(0, aquarium.height)

        # We'll update this in the simulation loop and send to clients for interpolation/rendering
        self.state = "idle"
        self.destination_x = self.x 
        self.destination_y = self.y
        self.speed = self.max_speed # This speed is dynamic

        # References for when the fish is in a certain state
        self.food = None # Food object
        self.predator = None # Fish object
        self.prey = None # Fish object
    
    def __idle(self, delta_time):
        # If the fish has reached its destination, pick a new one
        new_destination = False
        close_enough = 10 # Arbitrary distance to consider the fish at its destination
        if math.sqrt((self.destination_x - self.x)**2 + (self.destination_y - self.y)**2) < close_enough:
            self.destination_x = random.uniform(0, self.aquarium.width)
            self.destination_y = random.uniform(0, self.aquarium.height)
            self.direction = math.atan2(self.destination_y - self.y, self.destination_x - self.x)
            self.speed = random.uniform(self.max_speed/4, self.max_speed/2)
            new_destination = True
        # Move the fish towards its destination
        new_x = self.speed * math.cos(self.direction) * delta_time.total_seconds() + self.x
        new_y = self.speed * math.sin(self.direction) * delta_time.total_seconds() + self.y
        new_x = max(0, min(new_x, self.aquarium.width)) # Not necessary, but just in case
        new_y = max(0, min(new_y, self.aquarium.height))
        self.x = new_x
        self.y = new_y
        return(new_destination) # Tell the front-end to update the fish's heading

    def __feeding(self, delta_time):
        # Food is a Food object
        pass

    def __fleeing(self, delta_time):
        # Predator is a Fish object
        pass

    def __chasing(self, delta_time):
        # Prey is a Fish object
        pass

    def update(self, delta_time) -> bool:
        # Return whether the fish has changed (worth broadcasting)
        if self.state == "idle":
            return(self.__idle(delta_time))
        elif self.state == "feeding":
            return(self.__feeding(delta_time))
        elif self.state == "fleeing":
            return(self.__fleeing(delta_time))
        elif self.state == "chasing":
            return(self.__chasing(delta_time))
        else:
            Warning(f"Unknown fish state {self.state}")
            return(False)

    @property
    def summarize(self):
        return_dict = {
            "id": str(self.id),
            "update_time": datetime.datetime.now().timestamp() * 1000
        }
        properties_to_return = ["type", "name", "length", "state", "x", "y", "destination_x", "destination_y", "speed"]
        for prop in properties_to_return:
            return_dict[prop] = getattr(self, prop)
        return(return_dict)
    
class Food():
    def __init__(self, type, x, y, aquarium):
        self.type = type
        self.x = x
        self.y = y
        self.aquarium = aquarium
        self.id = uuid.uuid4()
        self.radius = 5
        
class Aquarium():
    def __init__(self, type):
        self.type = type

        if type not in aquarium_types:
            raise ValueError(f"Aquarium type {type} not found in aquarium_types")
        self.__dict__.update(aquarium_types[type])

        self.fishes = []

    def save(self, save_dir):
        fname = os.path.join(save_dir, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.type}.pkl")
        with open(fname, "wb") as f:
            pickle.dump(self, f)
