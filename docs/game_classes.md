# Python and JS classes for game state

In the backend, we have Python classes in order to simulate the Aquarium and its objects for the game. On each loop, every single item in the Aquarium is updated. Changes and updates are sent to the frontend, which has analogous classes to every backend class. The frontend classes are written in JavaScript and will use PixiJS to render the game. **Every class in the backend has a corresponding class in the frontend. Properties (that aren't private) will be the same in both classes.** This is not necessarily the case for methods or private classes, which are mainly used for simulation in the backend or rendering in the frontend. Propeties that are not shared between the backend and frontend classes are marked as such.

Some classes exist only in the backend (this will be specified). In this case, the frontend will implement the most specific class that it can. For example, for `Guppy` extends `Fish` extends `Thing`, the frontend will create a `Fish` object from the backend data. This is sufficient because the the frontend does not need to calculate the specific behavior of a `Guppy` object and properties like `texture_file` wil be sent to the frontend.

## `Aquarium` class

This is the main class that stores all items within the Aquarium. In the frontend, it extends the `PIXI.Container` class. 

### Properties

- `x` (float) (*frontend only*): The x-coordinate of the Aquarium, relative to the the PIXI application.

- `y` (float) (*frontend only*): The y-coordinate of the Aquarium, relative to the the PIXI application.

- `width` (float): The width of the Aquarium.

- `height` (float): The height of the Aquarium.

- `objects` (dict): A dictionary of all objects in the Aquarium. The keys are the `label` properties of the objects. The values are the objects themselves.

- `properties_to_broadcast` (list) (*backend only*): A list of names of properties that should be sent to the frontend when the Aquarium state is synced. Make sure nothing non-serializable or sensitive is included here.

- `summarize` (method) (*backend only*): Returns a dictionary of properties in `properties_to_broadcast`. Will also include `update_time` (ms since epoch that this method was called) and `objects` (a list of the labels of objects in `objects`).

### Methods

- `save` (save_dir: str) (*backend only*): Pickles the object (including all children in `objects`) to the directory specified by `save_dir`.

- `create_object` (class_name: str, **kwargs) (*backend only*): Creates an object of the specified class with the specified keyword arguments and adds it to the aquarium. Use this when we need to create a new object where the class isn't available in the current scope (e.g. in a function or method). This will work through the `command_queue` in `simulate.py`.

- `add_object` (object: Thing) (*backend only*): Adds an object to the Aquarium.

- `remove_object` (label: str) (*backend only*): Removes an object from the Aquarium. (Or use the `remove` method of the object itself; both will do the same thing.)


The *frontend* also has methods: `addThing`, `removeThing`, `updateThing`, and `syncEverything`. These methods are used to add, remove, update, and sync `Thing` objects in the Aquarium, when data from socketio is received. They use the data sent from the `summarize` method of `Thing` objects.

## `Tool` class

Tools are items that exist on a shelf above the Aquarium. These objects are static. They only exist in the frontend and extend the `PIXI.Sprite` class.

## `Thing` class

This is the base class for all objects in the Aquarium. This class is abstract and should not be instantiated directly. Later objects will inherit from this class. In the frontend, it extends the `PIXI.AnimatedSprite` class.

### Properties

- `aquarium` (Aquarium): The Aquarium object that the object is in.

- `label` (str(uuid4)): The unique identifier for the object. In the frontend, this will override the `label` property of the `PIXI.Sprite` class.

- `class_hierarchy` (list(str)): A list of strings that represent the class hierarchy of the object. For example, a `Guppy` object would have `['Thing', 'Fish', 'Guppy']`.

- `aspect_ratio` (float): The aspect ratio of the object. Can be used to dynmically calculate height! Set to `None` if you want to override the height calculation (make sure to set `_height`).

- `width` (float): The width of the object.

- `height` (float) (method): The height of the object. Method that returns the height of the object based on the aspect ratio and width. Set `_height` to a float to override this method.

- `x` (float): The x-coordinate of the object.

- `y` (float): The y-coordinate of the object.

- `speed` (float): The speed of the object in pixels per second (for objects that move).

- `destination_x` (float): The x-coordinate of the object's destination (for objects that move).

- `destination_y` (float): The y-coordinate of the object's destination (for objects that move).

- `lifetime` (float): The total number of seconds that the object will exist. This is used to remove the object after a certain amount of time. If this is `None`, the object will not be removed.

- `time_created` (float): The time that the object was created in milliseconds since epoch.

- `spritesheet_json` (str): The file path to the JSON file that describes the spritesheet of the object (e.g. `assets/things.json`). This is used in the frontend to create the `PIXI.AnimatedSprite` object and render it.

- `default_texture` (str): The name of the default sprite in the spritesheet (e.g. `fish.png`) if this object has no animations. This is used in the frontend to create the `PIXI.AnimatedSprite` object with only one frame.

- `default_animation` (str): The name of the default animation in the spritesheet (e.g. `idle`) if this object has animations. This is used in the frontend to create the `PIXI.AnimatedSprite` object with multiple frames.

- `updated_this_loop` (bool) (*backend only*): A flag that indicates whether the object has been "updated" in the current loop. This is used to determine whether the object should be broadcasted to the frontend.

- `properties_to_broadcast` (list) (*backend only*): A list of names of properties that should be sent to the frontend when the Aquarium state is synced. Make sure nothing non-serializable or sensitive is included here. Child classes should extend this list with their own properties.

- `summarize` (method) (*backend only*): Returns a dictionary of properties in `properties_to_broadcast`. Will also include `update_time` (ms since epoch that this method was called).

### Methods

- `click` (*backend only*): Called when the object is clicked in the frontend. This is coupled with the `click` event (check `docs/socketio.md` for more information).

- `update` (delta_time: float) (*backend only*): Updates the object's state. This method should be called on every loop of the Aquarium. The `delta_time` parameter is the time since the last loop in milliseconds. This should return a boolean indicating whether the object has changed and should be broadcasted to the frontend.

- `remove` (*backend only*): Removes the object from the Aquarium.

- `_move_to_destination` (delta_time: float) (*backend only*): Moves the object towards its destination. The `delta_time` parameter is the time since the last loop in milliseconds.

- `_is_colliding` (other: Thing) (*backend only*): Returns `True` if the object is colliding with another object. Otherwise, returns `False`.

- `_find_closest` (type: class_hierarchy(str)) (*backend only*): Returns the closest object of the specified type. Returns a tuple of the object and the distance to it.

# `Fish` class

This class represents a fish in the Aquarium. In both the backend and frontend, it extends the `Thing` class. In the backend, this class is also abstract, like `Thing`, and should not be instantiated directly. Subclasses of `Fish` (in `server/models/fish.py`) should be used instead.

### Properties

- `fish_name` (str): The name of the fish.

- `state` (str): The state of the fish. This can be `idle`, `feeding`, `fleeing`, or `chasing`.

- `health` (float): The health level of the fish. This is a float between 0 and 1. 0 is dead, and 1 is healthy.

- `happiness` (float): The happiness level of the fish. This is a float between 0 and 1. 0 is sad, and 1 is happy.

- `hunger` (float): The hunger level of the fish. This is a float between 0 and 1. 0 is not hungry at all, and 1 is starving. This is modeled by the following ODE: `dhunger/dt = +hunger_rate * speed`

- `hunger_rate` (float) (*backend only*): The rate at which the fish's hunger increases. This is a float between 0 and 1.

- `max_speed` (float) (*backend only*): The maximum speed of the fish in pixels per second.

- `food` (Food or Fish or None) (*backend only*): The food that the fish is currently eating or chasing. This is `None` if the fish is not eating or chasing anything. This is a reference to the object not a copy.

- `predator` (Fish or None) (*backend only*): The fish that is currently chasing this fish. This is `None` if the fish is not being chased. This is a reference to the object not a copy.

### Methods

- `update` (delta_time: float) (*backend only*): Changed from `Thing.update()`. Generally (unless changed by a subclass), this method will call houskeeping methods like `_calculate_hunger`, `_choose_state` then execute the state-specific methods (e.g. `_idle`, `_feed`, `_flee`). The `delta_time` parameter is the time since the last loop in milliseconds.

- `_calculate_hunger` (delta_time: float) (*backend only*): Updates the hunger level of the fish. The `delta_time` parameter is the time since the last loop in milliseconds.

- `_idle` (delta_time: float) (*backend only*): Called by `update` when the fish is in the `idle` state. Chooses a random destination and moves towards it. If the destination is reached, the fish will choose a new destination.

- `_feed` (delta_time: float) (*backend only*): Called by `update` when the fish is in the `feeding` state. Moves towards the `food` (set by `_choose_state`) and eats it.

- `_flee` (delta_time: float) (*backend only*): Called by `update` when the fish is in the `fleeing` state. Moves away from the `predator` (set by `_choose_state`).

- `_choose_state` (*backend only*): Changes the state of the fish. This method should also set references like `food` and `predator`. Will differ by subclass. Use this to porgram fish-specific behavior.

## `Food` class

Food is an object that can appear in the Aquarium. This class extends the `Thing` class in the backend and does not exist in the frontend. Specific types of food (e.g. `Pellet`, `Algae`) will extend this class.

### Properties

- `nutrition` (float): The amount of hunger that the food will satisfy.

## `Coin` class

Coins are things that can appear in the Aquarium. This class extends the `Thing` class in both the backend and frontend.

### Properties

- `value` (int): The value of the coin.
