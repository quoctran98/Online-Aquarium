// Aquariums are (PIXI) Containers for Things (Fish, Food, Coins, etc.)
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
        this.addThing = this.addThing.bind(this);
        this.removeThing = this.removeThing.bind(this);
        this.syncEverything = this.syncEverything.bind(this);
        this.updateThing = this.updateThing.bind(this);
    }

    insideAquarium(x, y) {
        return (x >= this.x && x <= this.x + this.width && y >= this.y && y <= this.y + this.height);
    }

    addThing(thingInput) {
        console.log(thingInput);
        // Loop through class_hierarchy backwards to find the most specific class that has a constructor
        let thingClass = Thing;
        for (let class_name of thingInput.class_hierarchy.reverse()) {
            try {
                thingClass = eval(class_name);
                break;
            } catch (e) {
                // Do nothing
            }
        }
        const thingTexture = PIXI.Assets.get(thingInput.texture_file);
        let thing = new thingClass(thingTexture, thingInput);
        this.addChild(thing);
        this.ticker.add(thing.handleTicker);
    }

    removeThing(thingLabel) {
        let thing = this.children.find(t => t.label === thingLabel);
        if (thing) {
            this.removeChild(thing);
        } else {
            console.log(`Thing ${thingLabel} not found in aquarium`);
        }
    }

    syncEverything(listOfThings) {
        const currentThingLabels = this.children.map(t => t.label);
        const serverThingLabels = listOfThings.map(t => t.label);
        // Remove things that are no longer in the server's list
        for (let thingLabel of currentThingLabels) {
            if (!serverThingLabels.includes(thingLabel)) { this.removeThing(thingLabel);}
        }
        // Add new things / update existing things
        for (let thingData of listOfThings) {
            this.updateThing(thingData);
        }
    }

    updateThing(thingData) {
        let thing = this.children.find(t => t.label === thingData.label);
        if (thing) {
            thing.serverUpdate(thingData);
        } else {
            this.addThing(thingData);
        }
    }
}

// Things are objects that can be added to the aquarium (Fish, Food, Coins, etc.)
// They all have common methods, so that the server can update them, etc. And a ticker
// thingInput is a JSON object with properties that are common to all things
class Thing extends PIXI.Sprite {
    constructor(texture, thingInput) {
        // Create a sprite with the given texture
        super(texture);
        // Unpack everything from the thingInput JSON object as properties
        this.label = thingInput.label; // Or else serverUpdate will fail
        this.serverUpdate(thingInput);

        // Bind external methods :)
        this.handleTicker = this.handleTicker.bind(this);
        this.serverUpdate = this.serverUpdate.bind(this);

        // Set the anchor to the center of the sprite and scale it (maintain aspect ratio)
        this.anchor.set(0.5);
        // Setting height and width in serverUpdate() later will scale the sprite
    }

    handleTicker(ticker) {
        // This is a placeholder for now
        // It should be overridden by subclasses for things that move
        this.interpolatePosition(ticker.deltaTime);
    }

    serverUpdate(thingInput) {
        // Make sure that this thingInput JSON object is for this Thing
        if (thingInput.label !== this.label) {
            console.log(`Thing.update() called with wrong thing label: ${thingInput.label} for ${this.label}`);
            return;
        }
        // Unpack everything from the thingInput JSON object as properties
        for (let key in thingInput) {
            this[key] = thingInput[key];
        }
        // Also server_x, server_y, should just be the x, y from the server
        // This is the only exception, I think?
        this.server_x = thingInput.x;
        this.server_y = thingInput.y;
    }

    interpolatePosition(deltaTime) {
        // Using the last known destination and postion, interpolate the thing's position
        const time_since_update = (Date.now() - this.update_time) / 1000; // in seconds
        const distance_covered = this.speed * time_since_update; // in pixels
        const total_distance = Math.sqrt((this.destination_x - this.server_x) ** 2 + (this.destination_y - this.server_y) ** 2);
        const progress = distance_covered / total_distance;
        if (progress >= 1) {
            // We have reached the destination
            this.x = this.destination_x;
            this.y = this.destination_y;
        } else {
            // Interpolate the fish's position
            this.x = this.server_x + progress * (this.destination_x - this.server_x);
            this.y = this.server_y + progress * (this.destination_y - this.server_y);
        }
    }
}


class Fish extends Thing {
    constructor(texture, fishInput) {
        super(texture, fishInput);
    }

    handleTicker(ticker) {
        this.interpolatePosition(ticker.deltaTime);
        this.animate();
    }

    animate() {
        // For now we'll just make the fish face the direction it's moving
        if (this.destination_x > this.x) {
            this.scale.x = Math.abs(this.scale.x);
        } else {
            this.scale.x = -Math.abs(this.scale.x);
        }
    }

}

// Food is individual food items that fish can eat
class Food extends Thing {
    constructor(texture, foodInput) {
        super(texture, foodInput);
    }

    handleTicker(ticker) {
        this.interpolatePosition(ticker.deltaTime);
    }
}


// Coins are collectible items that spawn from fish
class Coin extends Thing {
    constructor(texture, coinInput) {
        super(texture, coinInput);
    }

    handleTicker(ticker) {
        this.interpolatePosition(ticker.deltaTime);
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

export { Fish, Aquarium, Thing, Cursor, CursorContainer, Food, Coin };
