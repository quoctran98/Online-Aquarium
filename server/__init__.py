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

    # Define the command queue for the simulation (but don't start it yet)
    command_queue = queue.Queue()

    # Add funtions from helper.py to the Jinja environment
    # I want to do this in a more elegant way, but this works for now
    app.jinja_env.globals.update(format_number=format_number)
    app.jinja_env.globals.update(serialize_json=json.dumps)

    # Register HTTP routes
    from .routes.main import main as main_blueprint
    from .routes.api import api as api_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    # Regiser SocketIO events
    from .events import main as main_events
    from .events import aquarium as aquarium_events
    from .events import interactions as interactions_events
    main_events.register_events(socketio)
    aquarium_events.register_events(socketio, command_queue)
    interactions_events.register_events(socketio, command_queue)

    # Start the aquarium simulation
    socketio.start_background_task(aquarium_simulation, socketio, command_queue)

    # Make sure the app is running with the correct settings
    print(f"The current timezone is {pytz.timezone(settings.TIMEZONE).zone} ⏰")
    print(f"The current environment is {settings.ENVIRONMENT} 🌎")

    return(app)
