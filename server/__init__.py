from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_session import Session
from datetime import datetime, timezone
import pytz, json, queue, pickle, os

from server.simulate import aquarium_simulation
from server.helper import settings, format_number, dict_to_html
from server.models.user import User, GuestUser, UserManager
from server.models.game import Aquarium, Store, StoreItem

def create_app():

    # Set up Flask app
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.FLASK_SECRET_KEY

    # Set up Flask-Session
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Set up Flask-SocketIO
    socketio = SocketIO(app, manage_session=False)

    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.anonymous_user = GuestUser
    login_manager.login_view = "main.index"
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return(User.get_by_user_id(user_id))
               
    # Add funtions from helper.py to the Jinja environment
    # I want to do this in a more elegant way, but this works for now
    app.jinja_env.globals.update(format_number=format_number)
    app.jinja_env.globals.update(serialize_json=json.dumps)
    app.jinja_env.globals.update(User=User) # For initializing guest users
    app.jinja_env.globals.update(dict_to_html=dict_to_html)

    # Define the command queue, user manager, and chat manager for the site
    command_queue = queue.Queue()
    user_manager = UserManager()
    chat_manager = None # Placeholder for now

    # Start the aquarium simulation
    # saved_aquarium_fname = os.path.join(settings.AQUARIUM_SAVE_DIR, "20241106_200326_fishbowl.pkl")
    # aquarium = pickle.load(open(saved_aquarium_fname, "rb"))
    aquarium = Aquarium()
    socketio.start_background_task(aquarium_simulation, socketio, command_queue, user_manager, aquarium)

    # Set up the store
    store = Store()
    store.add_item("thermometer")

    # Register HTTP routes
    from .routes.main import main as main_blueprint
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    # Regiser SocketIO events
    from .events import main as main_events
    from .events import users as users_events
    from .events import aquarium as aquarium_events
    from .events import interactions as interactions_events
    from .events import chat as chat_events
    from .events import store as store_events   
    main_events.register_events(socketio)
    users_events.register_events(socketio, user_manager)
    chat_events.register_events(socketio, chat_manager)
    aquarium_events.register_events(socketio, command_queue)
    interactions_events.register_events(socketio, command_queue)
    store_events.register_events(socketio, command_queue, store)
                                   
    # Make sure the app is running with the correct settings
    print(settings)

    return(app)
