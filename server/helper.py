from pymongo import MongoClient
from pydantic_settings import BaseSettings
from flask_login import current_user
from flask_socketio import disconnect, emit
from flask import request
import json, functools

# Load settings from .env file
class Settings(BaseSettings):
    FLASK_SECRET_KEY:str
    ENVIRONMENT:str

    SESSION_FILE_DIR:str

    MONGODB_CONNECTION_STRING:str
    USERS_DATABASE:str

    APP_WIDTH:int
    APP_HEIGHT:int
    AQUARIUM_SAVE_DIR:str
    STORE_SAVE_DIR:str
    class Config:
        env_file = ".env"
settings = Settings()

# Load store items from JSON files
aquarium_types = {}
with open("server/data/aquarium_types.json") as f:
    aquarium_types = json.load(f)
store_items = {}
with open("server/data/store_items.json") as f:
    store_items = json.load(f)
tool_types = {}
with open("server/data/tools.json") as f:
    tool_types = json.load(f)

# Connect to MongoDB (and export the connection client and users collection)
mongo_client = MongoClient(settings.MONGODB_CONNECTION_STRING)
mongo_users_collection = mongo_client[settings.USERS_DATABASE].users
mongo_guests_collection = mongo_client[settings.USERS_DATABASE].guests 
# Clear the guests collection (once on startup, I guess?)
mongo_guests_collection.delete_many({})

###########################
# Helper functions below! #
###########################

# This is a function to format large numbers with commas.
# We use it mainly in Jinja templates.
def format_number(number):
    return("{:,}".format(number))

# We probably should have a better way to validate usernames but this is fine for now
def username_is_valid(username):
    return(username.isalnum() or "-" in username or "_" in username)

# Turn a dictionary to a list of HTML <p> tags for hidden data
def dict_to_html(data):
    return("\n".join([f"<p id='{key}'>{value}</p>" for key, value in data.items()]))

# Sanitize messages of HTML tags
def sanitize_message(message):
    return(message.replace("<", "&lt;").replace(">", "&gt;"))

# To use a @authenticated_only decorator on a SocketIO event
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return(f(*args, **kwargs))
    return(wrapped)
