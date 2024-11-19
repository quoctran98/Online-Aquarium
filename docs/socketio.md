# SocketIO Namespaces, Rooms, and Events for Aquarium Online

## `/aquarium` Namespace

**Broadcast the state of the aquarium to all clients**. This namespace doesn't require any authentication, and messages are broadcasted to all clients connected to the namespace, so that they can update their view of the aquarium.

Clients will connect on page load.

- `sync_everything` - Broadcasts the current state, position, and heading (and more) of **all** `Thing` objects in the aquarium as an **array** of JSON objects (one for each thing from the `.summarize` method of the `Thing` class). Take a look at `docs/classes.md` for more information on the `Thing` class.

- `update_thing` - Broadcasts the current state, position, and heading (and more) of **a single** `Thing` object in the aquarium as a JSON object from the `.summarize` method of the `Thing` class.

### `interactions` Namespace

**For clients to interact with the aquarium**. This namespace does not require any authentication and should be used for things that all users (including guests) can do (moving the cursor, feeding the fish, etc.). Messages sent from the client to the server are first validated then added to the command queue read by the main aquarium simulation loop. Results of these commands are not explicitly broadcased to all clients (except in some cases), but the state of the aquarium is updated and broadcasted to all clients connected to the `/aquarium` namespace.

Clients will connect on page load.

- `tap` - The client will send a message to the server when they click on the aquarium **without using a tool**. The message is a JSON object with the following fields. The whole JSON object is put into the command queue (with the command `tap`) for the main aquarium simulation loop to process.
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the tap.
    - `y` - The y-coordinate of the tap.
    - `timestamp` - The time the tap was made (in milliseconds since epoch).

- `pickup` - The client will send a message to the server when they click on an item the aquarium **to pick up a coin (or other thing)**. The message is a JSON object with the following fields. The whole JSON object is put into the command queue (with the command `pickup`) for the main aquarium simulation loop to process.
    - `thing_label` - The label of the thing being picked up.
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the coin pickup.
    - `y` - The y-coordinate of the coin pickup.
    - `timestamp` - The time the coin was picked up (in milliseconds since epoch).

- `click` - This is a more general version of the `pickup` event for an item in the aquarium. There's no functional difference but it's nice to specify!

- `use` - The client will send a message to the server when they click on the aquarium **using a tool**. This shouldn't be used for no tool, but the event can handle it. The message is a JSON object with the following fields. The whole JSON object is put into the command queue (with the command `use`) for the main aquarium simulation loop to process.
    - `tool` - The tool the client is using (this determines the action to take, null or None if no tool).
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the tool use.
    - `y` - The y-coordinate of the tool use.
    - `timestamp` - The time the coin was picked up (in milliseconds since epoch).

- `select` - The client will send a message to the server when they **select a tool from the shelf**. This is mainly used so other clients can render a cursor. The message is a JSON object with the following fields. *This event is verified then rebroadcasted to all clients connected to this namespace.*
    - `tool` - The tool_type (string) the client is selecting. (null or None if no tool).
    - `username` - The username of the client sending the message.
    - `timestamp` - The time the tool was selected (in milliseconds since epoch).

- `cursor` - Clients send their cursor position to the server. The message is a JSON object with the following fields. *This event is verified then rebroadcasted to all clients connected to this namespace.*
    - `event` - The event that triggered the cursor update ("mousemove", "mousedown", or "disconnect").
    - `username` - The username of the client sending the message.
    - `x` - The x-coordinate of the cursor.
    - `y` - The y-coordinate of the cursor.
    - `timestamp` - The time the cursor was updated (in milliseconds since epoch).

- `update_user` - Broadcasts the current state of a single user in the aquarium as a JSON object from the `summarize_public` method of the `User` class.

### `chat` Namespace

**Relay chat messages between clients.** This does not require any authentication -- guests can chat. Messages sent from the client to the server are broadcasted to all clients connected to the `/chat` namespace.

Clients will connect on page load.

- `user_connected` - Broadcasts the username of a client that has connected to the server. The message just contains the username of the client that connected.

- `user_disconnected` - Broadcasts the username of a client that has disconnected from the server. The message just contains the username of the client that disconnected.

- `new_message` - Clients a message to the server which relays this message to all clients connected to the `/chat` namespace. The message is a JSON object with the following fields:
    - `username` - The username of the client sending the message.
    - `message` - The message sent by the client.
    - `timestamp` - The time the message was sent (in milliseconds since epoch).

### `store` Namespace

**For clients to interact with the store**. The main use is for clients to add contributions to items in the store.

Clients will connect on page load.

- `contribute` - Clients will send a message to the server when they contribute funds to an item in the store. The message is a JSON object with the following fields:
    - `item_label` - The label of the item in the store.
    - `username` - The username of the client adding the contribution.
    - `amount` - The amount of the contribution.

- `update_item` - Broadcasts the current state of a single item in the store as a JSON object from the `summarize` method of the `StoreItem` class.

- `summarize_store` - Broadcasts the current state of all items in the store as an **array** of JSON objects (one for each item from the `summarize` method of the `StoreItem` class).

- `get_store` - Clients will send a message to the server to get the current state of all items in the store. The server will respond with a `summarize_store` message.

### `users` Namespace

**For dynamic data about users to be exchanged between clients and the server**. This namespace is for clients to get information about other users in the aquarium. And for users to change their own information.

Clients will connect on page load.

- `user_connected` - Broadcasts the `summarize_public` method of the `User` class for a user that has connected to the namespace (as a proxy for the website).  

- `user_disconnected` - Broadcasts the `summarize_public` method of the `User` class for a user that has disconnected from the namespace (as a proxy for the website).

- `update_user` - Broadcasts the `summarize_public` method of the `User` class for a user if something about them has changed.