# SocketIO Namespaces, Rooms, and Events for Aquarium Online
## Namespaces
- `/` - The default namespace; used for general server-wide events and messages.

- `/aquarium` - Used by the server to broadcast things like fish movememnt, etc. 

- `/interactions` - Used for interactions between the user and the aquarium, such as feeding, etc. (should this be in the aquarium namespace?)

- `/chat` - Used for chat messages.

## Events

### `aquarium` Namespace

- `fishes` - Broadcasts the current state and position of all fishes in the aquarium as an array of fish objects:
    ```json
    [
        {
            "id": 1,
            "name": "Nemo",
            "type": "clownfish",
            "position": {
                "x": 100,
                "y": 100
            }
        },
        {
            "id": 2,
            "name": "Dory",
            "type": "blue tang",
            "position": {
                "x": 200,
                "y": 200
            }
        }
    ]
    ```



