# SocketIO Namespaces, Rooms, and Events for Aquarium Online

## `/aquarium` Namespace

This namespace is used to broadcast the state of the aquarium to all clients connected to the `/aquarium` namespace. This namespace doesn't require any authentication, and messages are broadcasted to all clients connected to the namespace, so that they can update their view of the aquarium.

- `sync_fishes` - Broadcasts the current state, position, and heading of **all** fishes in the aquarium as an array of JSON objects (one for each fish from the `.summarize() method of the `Fish` class) with the following fields:
    - `id` (uui4, str) - The unique identifier of the fish
    - `type` (str) - The type of the fish (listed in `/server/data/fish_types.json`)
    - `name`(str) - The name of the fish
    - `length` (int) - The length of the fish (in pixels)
    - `state` (str) - The state of the fish (either "swimming" or "eating")
    - `x` (int) - The x-coordinate of the fish relative to the aquarium
    - `y` (int) - The y-coordinate of the fish relative to the aquarium
    - `destination_x` (int) - The x-coordinate of the fish's destination
    - `destination_y` (int) - The y-coordinate of the fish's destination
    - `speed` (float) - The speed of the fish (in pixels per second)
    - `update_time` (int) - The time the fish was last updated (in milliseconds since epoch)

- `update_fish` - Broadcasts the current state, position, and heading of **a single** fish (those that have changed headings, states, or whatever) in the aquarium a JSON object (NOT an array) with the same fields as `sync_fishes`.

### `interactions` Namespace

This namespace is used to allow authenticated clients (using Flask login) to interact with the aquarium. Messages sent from the client to the server are first validated then added to the command queue read by the main aquarium simulation loop. Results of these commands are not explicitly broadcased to all clients, but the state of the aquarium is updated and broadcasted to all clients connected to the `/aquarium` namespace.

- `my_cursor` - Clients send their cursor position to the server. The message is a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the cursor.
    - `y` - The y-coordinate of the cursor.

- `sync_cursors` - Broadcasts the current position of all cursors in the aquarium as an array of JSON objects (one for each cursor) with the following fields:
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the cursor.
    - `y` - The y-coordinate of the cursor.

- `update_cursor` - Broadcasts the current position of a single cursor in the aquarium as a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the cursor.
    - `y` - The y-coordinate of the cursor.

- `feed` - Broadcasts a message to feed the fishes in the aquarium. The message is a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `food` - The type of food to feed the fishes (either "pellet" or "flake").
    - `x` - The x-coordinate of the food drop.
    - `y` - The y-coordinate of the food drop.

### `chat` Namespace

This namespace is used to allow authenticated clients to chat with each other. Messages sent from the client to the server are broadcasted to all clients connected to the `/chat` namespace.

- `message` - Broadcasts a message to all clients connected to the `/chat` namespace. The message is a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `message` - The message sent by the client.


