# Python and JS classes for game state

In the backend, we have Python classes in order to simulate the Aquarium and its objects for the game. On each loop, every single item in the Aquarium is updated. Changes and updates are sent to the frontend, which has analogous classes to every backend class. The frontend classes are written in JavaScript and will use PixiJS to render the game. **Every class in the backend has a corresponding class in the frontend. Properties (that aren't private) will be the same in both classes.** This is not necessarily the case for methods or private classes, which are mainly used for simulation in the backend or rendering in the frontend. Propeties that are not shared between the backend and frontend classes are marked as such.

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

- `addThing` (method) (*backend only*): Adds a 

### Methods

- `save` (save_dir: str) (*backend only*): Pickles the object (including all children in `objects`) to the directory specified by `save_dir`.

The *frontend* also has methods: `addThing`, `removeThing`, `updateThing`, and `syncEverything`. These methods are used to add, remove, update, and sync `Thing` objects in the Aquarium, when data from socketio is received. They use the data sent from the `summarize` method of `Thing` objects.

## `Thing` class

This is the base class for all objects in the Aquarium. This class is abstract and should not be instantiated directly. Later objects will inherit from this class. In the frontend, it extends the `PIXI.Sprite` class.

### Properties

- `aquarium` (Aquarium): The Aquarium object that the object is in.

- `label` (str(uuid4)): The unique identifier for the object. In the frontend, this will override the `label` property of the `PIXI.Sprite` class.

- `class_hierarchy` (list(str)): A list of strings that represent the class hierarchy of the object. For example, a `Guppy` object would have `['Thing', 'Fish', 'Guppy']`.

- `width` (float): The width of the object.

- `height` (float): The height of the object.

- `x` (float): The x-coordinate of the object.

- `y` (float): The y-coordinate of the object.

- `speed` (float): The speed of the object in pixels per second (for objects that move).

- `destination_x` (float): The x-coordinate of the object's destination (for objects that move).

- `destination_y` (float): The y-coordinate of the object's destination (for objects that move).

- `time_created` (float): The time that the object was created in milliseconds since epoch.

- `texture` (str): The file path to the texture of the object (e.g. `assets/fish/godlfish.png`). This is used in the frontend to create the `PIXI.Sprite` object and render it.

- `properties_to_broadcast` (list) (*backend only*): A list of names of properties that should be sent to the frontend when the Aquarium state is synced. Make sure nothing non-serializable or sensitive is included here. Child classes should extend this list with their own properties.

- `summarize` (method) (*backend only*): Returns a dictionary of properties in `properties_to_broadcast`. Will also include `update_time` (ms since epoch that this method was called).

### Methods

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

- `hunger` (float) (*backend only*): The hunger level of the fish. This is a float between 0 and 1. 0 is not hungry at all, and 1 is starving. This is modeled by the following ODE: `dhunger/dt = -hunger_decay_rate * speed`

- `hunger_decay_rate` (float) (*backend only*): The rate at which the fish's hunger decreases in hunger units per second.

- `max_speed` (float) (*backend only*): The maximum speed of the fish in pixels per second.

- `food` (Food or Fish or None) (*backend only*): The food that the fish is currently eating or chasing. This is `None` if the fish is not eating or chasing anything. This is a reference to the object not a copy.

- `predator` (Fish or None) (*backend only*): The fish that is currently chasing this fish. This is `None` if the fish is not being chased. This is a reference to the object not a copy.

### Methods

- `idle` (*backend only*): The fish just swims around randomly.

- `feed` (food: Food or Fish) (*backend only*): The fish swims towards and eats the food.

- `_calculate_hunger` (delta_time: float) (*backend only*): Updates the hunger level of the fish. The `delta_time` parameter is the time since the last loop in milliseconds.

- `_choose_state` (*backend only*): Changes the state of the fish. Will differ by subclass.

## `Coin` class

Coins are things that can appear in the Aquarium. This class extends the `Thing` class in both the backend and frontend.

### Properties

- `value` (int): The value of the coin.