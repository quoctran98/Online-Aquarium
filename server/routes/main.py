from flask import request, session, Blueprint, render_template, send_from_directory
from flask_login import current_user
from flask_socketio import emit

from server.models.user import User, GuestUser
from server.helper import settings

import random, uuid

main = Blueprint("main", __name__)

@main.route("/robots.txt")
def robots():
    return(render_template("robots.txt"))

@main.route("/")
def index():
    return(render_template("index.html"))

# I'm not sure this is the right way to load assets for PixiJS but it should work 
@main.route("/assets/<path:path>")
def assets(path):
    return(send_from_directory("static/assets", path))

# Right now it's just for tools.json
@main.route("/data/<path:path>")
def data(path):
    return(send_from_directory("data", path))
