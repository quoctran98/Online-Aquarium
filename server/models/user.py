from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from server.helper import settings, mongo_users_collection, mongo_guests_collection
import uuid, datetime

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
        
    def subtract_money(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            return(False)
        if amount > self.money:
            return(False)
        self.money = round(self.money - amount, 2)
        self.save()
        return(True)
        
    def save(self):
        mongo_users_collection.update_one({"user_id": self.user_id}, {"$set": self.summarize_private})

    @property
    def summarize_private(self):
        # Return all properties of the user (for saving to MongoDB)
        return({key: value for key, value in self.__dict__.items() if key not in ["_id"]})
    
    @property
    def summarize_public(self):
        return({
            "username": self.username,
            "money": self.money
        })
    
class GuestUser(AnonymousUserMixin):
    def __init__(self, username=None, user_id=None, _id=None, **kwargs):
        self.user_id = uuid.uuid4().hex if user_id is None else user_id
        self.mongo_id = None if _id is None else str(_id)
        self.username = "Guest-" + str(self.user_id[:8]) if username is None else username

        # Other user attributes (For game stuff that we might want to save)
        self.money = kwargs.get("money", 0)
    
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
    # @property
    # def get_id(self):
    #     return(self.user_id) # Hopefully won't cause any issues...
    # This broke it in @login_manager.request_loader... (https://stackoverflow.com/questions/43602084/flask-login-raises-typeerror-int-object-is-not-callable)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        data = mongo_guests_collection.find_one({"user_id": user_id})
        if data:
            return(cls(**data))
        return(None)
    
    @classmethod
    def new_guest(cls):
        new_guest = cls()
        mongo_guests_collection.insert_one(new_guest.summarize_private)
        return(new_guest)
    
    def subtract_money(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            return(False)
        amount = round(amount, 2)
        if amount > self.money:
            return(False)
        self.money = round(self.money - amount, 2)
        self.save()
        return(True)
    
    def save(self):
        mongo_guests_collection.update_one({"user_id": self.user_id}, {"$set": self.summarize_private})

    @property
    def summarize_private(self):
        # Return all properties of the user (for saving to MongoDB)
        return({key: value for key, value in self.__dict__.items() if key not in ["_id"]})

    @property
    def summarize_public(self):
        return({
            "username": self.username,
            "money": self.money
        })
    
# This is a weird abstract class to manage users from within the simulation
# I don't think I really need it, but it's more clean?
class UserManager():
    def __init__(self):
        self.online_users = {} # Keys are username, values are User or GuestUser objects
        self.guest_users = {} # Keys are username, values are GuestUser objects
        # Maybe we should use a database to store guest users?

    # These properties only matter for users that are currently online -- no need to save them
    def attach_temp_properties(self, user):
        user.tool_selected = None
        user.cursor_position = None # (x, y) tuple

    def get_by_username(self, username):
        user = User.get_by_username(username)
        if user:
            return(user)
        elif username in self.guest_users:
            return(self.guest_users[username])
        return(None)
    
    def user_connected(self, user):
        if not user.is_authenticated:
            self.guest_users[user.username] = user
        user.last_seen = datetime.datetime.now().timestamp() # ms since epoch
        self.online_users[user.username] = user

    def user_disconnected(self, user):
        user.last_seen = datetime.datetime.now().timestamp()
        if user.is_authenticated:
            user.save()
        if (user.username in self.online_users):
            del self.online_users[user.username]
