from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from server.helper import settings, mongo_users_collection
import uuid

class User(UserMixin):
    def __init__(self, username, hashed_password, user_id=None, _id=None, **kwargs):
        # We might need to implement user_id this way for Flask-Login? Yeah!
        self.user_id = uuid.uuid4().hex if user_id is None else str(user_id)
        self.mongo_id = None if _id is None else str(_id) # MongoDB _id
        self.username = username
        self.hashed_password = hashed_password

        # Other user attributes (For game stuff that we might want to save)
        self.money = kwargs.get("money", 0)

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
    def signup(cls, username, unhashed_password, from_guest=False):
        user = cls.get_by_username(username)
        if user: # User already exists
            return(False)
        else: # Create a new user
            hashed_password = generate_password_hash(unhashed_password)
            mongo_users_collection.insert_one({
                "username": username, 
                "hashed_password": hashed_password,
                "user_id": uuid.uuid4().hex})
            return(True)
        
    def save(self):
        mongo_users_collection.update_one({"user_id": self.user_id}, {"$set": self.serialize_private})

    @property
    def serialize_private(self):
        # Return all properties of the user (for saving to MongoDB)
        return({key: value for key, value in self.__dict__.items() if key not in ["_id"]})
    
    @property
    def serialize_public(self):
        return({
            "username": self.username,
            "user_id": self.user_id,
            "money": self.money
        })
    
class GuestUser(AnonymousUserMixin):
    def __init__(self):
        self.user_id = uuid.uuid4().hex
        self.username = "Guest-" + str(self.user_id[:8])
        self.money = 0
    
    # Make these properties to override the default values
    @property
    def is_authenticated(self):
        return(False) # Guest users are not authenticated!
    @property
    def is_active(self):
        return(True)
    @property
    def is_anonymous(self):
        return(True) # Guest users are anonymous!
    @property
    def get_id(self):
        return(self.user_id) # Hopefully won't cause any issues...

    @property
    def serialize_public(self):
        return({
            "username": self.username,
            "user_id": self.user_id,
            "money": self.money
        })
