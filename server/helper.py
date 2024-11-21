from pymongo import MongoClient
from pydantic_settings import BaseSettings
import boto3
from botocore.client import Config
from flask_login import current_user
from flask_socketio import disconnect, emit
from flask import request
import json, functools, pickle
from io import BytesIO

# Load settings from .env file
class Settings(BaseSettings):
    FLASK_SECRET_KEY:str
    ENVIRONMENT:str

    SESSION_FILE_DIR:str

    MONGODB_CONNECTION_STRING:str
    USERS_DATABASE:str

    S3_AQUARIUM_SAVE_DIR:str
    S3_STORE_SAVE_DIR:str
    S3_BUCKET_NAME:str
    S3_ACCESS_KEY:str
    S3_SECRET_KEY:str

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

# Connect to the DigitalOcean Spaces (S3) bucket
s3_session = boto3.session.Session()
s3_client = s3_session.client("s3", 
                              region_name="sfo3",
                              endpoint_url="https://aquarium-bucket.sfo3.digitaloceanspaces.com", 
                              aws_access_key_id=settings.S3_ACCESS_KEY, 
                              aws_secret_access_key=settings.S3_SECRET_KEY)

#####################
# Decorators below! #
#####################

# To use a @confirm_user decorator on a SocketIO event
def confirm_user(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # Confirm that the username in the data matches the current user's username
        if args[0]["username"] == current_user.username:
            return(f(*args, **kwargs))
        else:
            print(f"User {current_user.username} tried to perform an action as {args[0]['username']} in {f.__name__}")
            disconnect()
    return(wrapped)

# To use a @authenticated_only decorator on a SocketIO event
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return(f(*args, **kwargs))
    return(wrapped)

# To save a PICKLE file to the DigitalOcean Spaces bucket
def save_to_s3(pickle, filename, directory, bucket=settings.S3_BUCKET_NAME):
    # Don't save to S3 if we're in a local environment
    if settings.ENVIRONMENT == "local":
        with open(f"./server/{directory}{filename}", "wb") as f:
            f.write(pickle)
    else:
        s3_client.put_object(Bucket=bucket, Key=f"{directory}{filename}", Body=pickle)

#######################
# S3 functions below! #
#######################
    
# To load a PICKLE file from the DigitalOcean Spaces bucket
def load_from_s3(filename, directory, bucket=settings.S3_BUCKET_NAME):
    response = s3_client.get_object(Bucket=bucket, Key=f"{directory}{filename}")
    return(pickle.load(BytesIO(response["Body"].read())))

# To load the most recent PICKLE file from the DigitalOcean Spaces bucket
def load_latest_from_s3(directory, bucket=settings.S3_BUCKET_NAME):
    # objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=directory)["Contents"]
    # latest_key = max(objects, key=lambda obj: obj["LastModified"])["Key"]
    # ^ THIS DOESN'T WORK FOR SOME REASON -- READ TODO.MD
    # For now, we'll build the endpoing manually (since we're also saving a latest.pkl file every time)
    latest_key = f"{directory}latest.pkl"
    # Download and deserialize the pickle file
    response = s3_client.get_object(Bucket=bucket, Key=latest_key)
    return(pickle.load(BytesIO(response["Body"].read())))


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
