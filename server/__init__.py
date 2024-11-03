from flask import Flask
from flask_socketio import SocketIO
from datetime import datetime, timezone
import pytz, json, queue

from server.simulate import aquarium_simulation
from server.helper import settings, format_number
from server.models import Fish

def create_app():

    # Set up Flask app and socketio
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.FLASK_SECRET_KEY
    socketio = SocketIO(app)

    # Start the aquarium simulation
    command_queue = queue.Queue()
    socketio.start_background_task(aquarium_simulation, socketio, command_queue)

    # Add funtions from helper.py to the Jinja environment
    # I want to do this in a more elegant way, but this works for now
    app.jinja_env.globals.update(format_number=format_number)
    app.jinja_env.globals.update(serialize_json=json.dumps)

    # Blueprint for main routes from routes/main.py
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Blueprint for API routes from routes/api.py
    from .routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Register events from events/aquarium.py
    from .events import aquarium
    aquarium.register_events(socketio, command_queue)

    # Make sure the app is running with the correct settings
    print("Routes registered! 🌐")
    print(f"The current environment is {settings.ENVIRONMENT} 🌎")

    return(app)
