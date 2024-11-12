# SocketIO Namespaces, Rooms, and Events for Aquarium Online

## `/aquarium` Namespace

**Broadcast the state of the aquarium to all clients**. This namespace doesn't require any authentication, and messages are broadcasted to all clients connected to the namespace, so that they can update their view of the aquarium.

Clients will connect on page load.

- `sync_everything` - Broadcasts the current state, position, and heading (and more) of **all** `Thing` objects in the aquarium as an **array** of JSON objects (one for each thing from the `.summarize` method of the `Thing` class). Take a look at `docs/classes.md` for more information on the `Thing` class.

- `update_thing` - Broadcasts the current state, position, and heading (and more) of **a single** `Thing` object in the aquarium as a JSON object from the `.summarize` method of the `Thing` class.

### `interactions` Namespace

**For clients to interact with the aquarium**. This namespace does not require any authentication and should be used for things that all users (including guests) can do (moving the cursor, feeding the fish, etc.). Messages sent from the client to the server are first validated then added to the command queue read by the main aquarium simulation loop. Results of these commands are not explicitly broadcased to all clients (except in some cases), but the state of the aquarium is updated and broadcasted to all clients connected to the `/aquarium` namespace.

Clients will connect on page load.

- `my_cursor` - Clients send their cursor position to the server. The message is a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the cursor.
    - `y` - The y-coordinate of the cursor.
    - `event` - The event that triggered the cursor update ("mousemove", "mousedown", or "disconnect").

- `update_cursor` - Broadcasts the current position of a single cursor in the aquarium as a JSON object with the same fields as the data sent in the `my_cursor` message.

- `user_connected` - Broadcasts the username of a client that has connected to the server. The message just the username of the client that connected. For now usernames are just the socket id.

- `user_disconnected` - Broadcasts the username of a client that has disconnected from the server. The message just the username of the client that disconnected. For now usernames are just the socket id.

- `click` - The client will send a message to the server when they click on an item in the aquarium. The message is a JSON object with the following fields. The whole JSON object is put into the command queue for the main aquarium simulation loop to process.
    - `username` - The username of the client sending the message.
    - `label` - The label of the item clicked on.
    - `timestamp` - The time the coin was picked up (in milliseconds since epoch).

- `feed` - Broadcasts a message to feed the fishes in the aquarium. The message is a JSON object with the following fields. The whole JSON object is put into the command queue for the main aquarium simulation loop to process.
    - `username` - The username of the client sending the message.
    - `food` - The type of food to feed the fishes (either "pellet" or "flake").
    - `x` - The x-coordinate of the food drop.
    - `y` - The y-coordinate of the food drop.

- `update_user` - Broadcasts the current state of a single user in the aquarium as a JSON object from the `summarize_public` method of the `User` class.

### `interactions-auth` Namespace

**For authenticated clients to interact with the aquarium**. This namespace is for the same purposes and has the same behavior as the `/interactions` namespace, but is only accessible to authenticated clients for actions that require authentication (like bidding on new fishes, betting, etc.).

Clients will only connect if they are authenticated. Messages will be ignored if the client is not authenticated.


### `chat` Namespace

**Relay chat messages between clients.** This does not require any authentication -- guests can chat. Messages sent from the client to the server are broadcasted to all clients connected to the `/chat` namespace.

Clients will connect on page load.

- `user_connected` - Broadcasts the username of a client that has connected to the server. The message just contains the username of the client that connected.

- `user_disconnected` - Broadcasts the username of a client that has disconnected from the server. The message just contains the username of the client that disconnected.

- `new_message` - Clients a message to the server which relays this message to all clients connected to the `/chat` namespace. The message is a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `message` - The message sent by the client.
    - `timestamp` - The time the message was sent (in milliseconds since epoch).
