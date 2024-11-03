from pydantic_settings import BaseSettings
from flask import request
import json

# Load settings from .env file
class Settings(BaseSettings):
    FLASK_SECRET_KEY:str
    ENVIRONMENT:str
    APP_WIDTH:int
    APP_HEIGHT:int
    SIMULATION_TICK:float
    class Config:
        env_file = ".env"
settings = Settings()

# Load fish and aquarium stats from the JSON file
fish_stats = {}
with open("server/data/fish_stats.json") as f:
    fish_stats = json.load(f)
aquarium_stats = {}
with open("server/data/aquarium_stats.json") as f:
    aquarium_stats = json.load(f)

# Connect to MongoDB users database
# users_db = client[settings.USERS_DB_NAME]
# active_users_coll = users_db.active_users
# old_users_coll = users_db.old_users

###########################
# Helper functions below! #
###########################

# This is a function to format large numbers with commas.
# We use it mainly in Jinja templates.
def format_number(number):
    return("{:,}".format(number))

