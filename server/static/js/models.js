// Fish are fish in the aquarium
class Fish extends PIXI.Sprite {
    constructor(texture, fish_input) {
        super(texture);

        this.label = fish_input.id; // Shared by server and PIXI
        this.fish_name = fish_input.name; // name is a default property of the Sprite class (deprecated)

        // Fish simulation properties from the server
        this.type = fish_input.type;
        this.state = fish_input.state;

        // Bind handleTicker and serverUpdate methods to this object so we can call it externally
        this.handleTicker = this.handleTicker.bind(this);
        this.serverUpdate = this.serverUpdate.bind(this);

        // Server position and destination used for movement interpolation
        this._server_x = fish_input.x;
        this._server_y = fish_input.y;
        this._destination_x = fish_input.destination_x;
        this._destination_y = fish_input.destination_y;
        this._speed = fish_input.speed;
        this._server_update_time = fish_input.update_time;
        this._local_update_time = this.update_time; // last time we updated the fish locally

        // Now we can set properties for the PIXI Sprite object
        this.x = this.server_x;
        this.y = this.server_y;
        // Scale the sprite to the desired length (fish_input.length is length in pixels)
        this.scale.x = fish_input.length / this.texture.width;
        this.scale.y = fish_input.length / this.texture.height;
    }

    handleTicker(ticker) {
        this.interpolatePosition(ticker.deltaTime);
        this.animate();
    }

    animate() {
        // For now we'll just make the fish face the direction it's moving
        if (this._destination_x > this.x) {
            this.scale.x = Math.abs(this.scale.x);
        } else {
            this.scale.x = -Math.abs(this.scale.x);
        }
    }

    interpolatePosition(deltaTime) {
        // Using the last known destination and postion,
        // we can use the speed and time since the last server update to interpolate the fish's position
        // deltaTime is the time since the last frame in milliseconds (from the ticker) -- not really needed
        const time_since_update = (Date.now() - this._server_update_time) / 1000; // in seconds
        const distance_covered = this._speed * time_since_update; // in pixels
        const total_distance = Math.sqrt((this._destination_x - this._server_x) ** 2 + (this._destination_y - this._server_y) ** 2);
        const progress = distance_covered / total_distance;
        if (progress >= 1) {
            // We have reached the destination
            this.x = this._destination_x;
            this.y = this._destination_y;
        } else {
            // Interpolate the fish's position
            this.x = this._server_x + progress * (this._destination_x - this._server_x);
            this.y = this._server_y + progress * (this._destination_y - this._server_y);
        }
    }
    
    serverUpdate(fish_input) {
        // Make sure that this fish_input JSON object is for this fish
        if (fish_input.id !== this.label) {
            console.log(`Fish.update() called with wrong fish id: ${fish_input.id}`);
            return;
        }

        // Update the fish's data with new fish_input
        // Maybe we should do it so that only changed fields are sent and we just unpack them here
        this.state = fish_input.state;
        this.x = fish_input.x;
        this.y = fish_input.y;
        this._server_x = fish_input.x;
        this._server_y = fish_input.y;
        this._speed = fish_input.speed;
        this._destination_x = fish_input.destination_x;
        this._destination_y = fish_input.destination_y;
        this._server_update_time = fish_input.update_time;
    }

}

// Aquariums are (PIXI) Containers for Fish
class Aquarium extends PIXI.Container {
    constructor() {
        super();

        this.x = 0;
        this.y = 100;
        this.width = 500;
        this.height = 500;

        this.ticker = new PIXI.Ticker();
        this.ticker.start();

        // Bind all methods that we need to call externally
        this.addFish = this.addFish.bind(this);
        this.syncFishes = this.syncFishes.bind(this);
        this.updateFish = this.updateFish.bind(this);
        this.removeFish = this.removeFish.bind(this);
    }

    // Add a fish to the aquarium
    addFish(fish_data) {
        const fish_type = fish_data.type;
        // We should use a sprite sheet for the fish textures...
        let fish = new Fish(PIXI.Assets.get(`assets/fish/${fish_type}.png`), fish_data);
        this.addChild(fish);
        this.ticker.add(fish.handleTicker);
      }

    // Sync the position and state of all Fish in the aquarium with server data
    syncFishes(fishes) {
        const current_fish_ids = this.children.map(f => f.label);
        const server_fish_ids = fishes.map(f => f.id);
        
        // Remove fish that are no longer in the server's list
        for (let fish_id of current_fish_ids) {
            if (!server_fish_ids.includes(fish_id)) { this.removeFish(fish_id);}
        }

        // Add new fish / update existing fish
        for (let fish_data of fishes) {
            this.updateFish(fish_data);
        }
    }

    // Update a single fish when the server broadcasts an update or a sync
    updateFish(fish_data) {
        let fish = this.children.find(f => f.label === fish_data.id);
        if (fish) {
          fish.serverUpdate(fish_data);
        } else {
          this.addFish(fish_data); // If the fish isn't in the list, add it!
        }
    }

    // Remove a fish from the aquarium
    removeFish(fish_id) {
        let fish = aquarium.children.find(f => f.label === fish_id);
        if (fish) {
          this.removeChild(fish);
        } else {
          console.log(`Fish ${fish_id} not found in aquarium`);
        }
    }

}

// Things are objects on the shelf that can be interacted with
class Thing extends PIXI.Sprite {
    constructor(texture) {
        super(texture);
    }
}

// Cursors are other players' cursors (will also show them picking up items)
class Cursor extends PIXI.Sprite {
    constructor(texture, cursor_input) {
        super(texture);
        this.label = cursor_input.username;
        this.username = cursor_input.username; // Just in case I forgot to change something
        this.scale.x = 30 / this.texture.width;
        this.scale.y = 30 / this.texture.height;
        this.anchor.set(0.5);
    }

    serverUpdate(cursor_input) {
        // Make sure that this cursor_input JSON object is for this cursor
        if (cursor_input.username !== this.label) {
            console.log(`Cursor.update() called with wrong cursor username: ${cursor_input.username}`);
            return;
        } else {
            this.x = cursor_input.x;
            this.y = cursor_input.y;
        }
    }
}

// CursorContainer is a container for all other players' cursors (this is very similar to the Aquarium class)
class CursorContainer extends PIXI.Container {
    constructor(username) {
        super();

        // The username is the socket ID for now :)
        // Mayber user data should be some global object that we can access from anywhere
        this.username = username;

        // Bind all methods that we (might) need to call externally
        this.addCursor = this.addCursor.bind(this);
        this.updateCursor = this.updateCursor.bind(this);
        this.removeCursor = this.removeCursor.bind(this);

    }

    addCursor(cursor_data) {
        // Don't add if it's the current user's cursor
        if (cursor_data.username === this.username) { return; }
        let cursor = new Cursor(PIXI.Assets.get("assets/cursor.png"), cursor_data);
        this.addChild(cursor);
        return(cursor);
      }

    updateCursor(cursor_data) {
        // Don't update if it's the current user's cursor
        if (cursor_data.username === this.username) { return; }
        let cursor = this.children.find(c => c.label === cursor_data.username);
        if (!cursor) { // If the cursor isn't in the list, add it!
            cursor = this.addCursor(cursor_data); 
        }
        cursor.serverUpdate(cursor_data);
    }

    removeCursor(username) {
        // This is broken right now
        console.log(`This session's socket ID: ${this.username}`);
        console.log(`Cursor ID to remove: ${username}`);
        console.log(`Cursors: ${this.children.map(c => c.label)}`);
        let cursor = this.children.find(c => c.label === username);
        if (cursor) {
            this.removeChild(cursor);
        } else {
          console.log(`Cursor ${username} not found in cursors`);
        }
      }
}

// Food is individual food items that fish can eat
class Food extends PIXI.Sprite {
    constructor(texture) {
        super(texture);
    }
}

export { Fish, Aquarium, Thing, Cursor, CursorContainer };
