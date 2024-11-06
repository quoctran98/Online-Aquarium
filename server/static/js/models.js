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

export { Fish, Thing, Cursor };