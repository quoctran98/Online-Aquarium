from flask import Flask, request, jsonify, Blueprint, render_template, send_from_directory
from flask_socketio import SocketIO, emit

from server.helper import settings

import random

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return(render_template("index.html"))

# I'm not sure this is the right way to load assets for PixiJS but it should work 
@main.route("/assets/<path:path>")
def assets(path):
    return(send_from_directory("static/assets", path))

@main.route("/robots.txt")
def robots():
    return(render_template("robots.txt"))
