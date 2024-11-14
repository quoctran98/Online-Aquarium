import { interactionsSocket } from "../sockets.js";
import { parse_p_tags } from "../utils.js";

const userInfo = parse_p_tags("user-info");

// Aquariums are (PIXI) Containers for Things (Fish, Food, Coins, etc.)
class Aquarium extends PIXI.Container {
    constructor({ x, y, width, height }) {
        super();
        this.sortableChildren = true;
        
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;

        this.ticker = new PIXI.Ticker();
        this.ticker.start();

        // Bind all methods that we need to call externally
        this.addThing = this.addThing.bind(this);
        this.removeThing = this.removeThing.bind(this);
        this.syncEverything = this.syncEverything.bind(this);
        this.updateThing = this.updateThing.bind(this);
    }

    insideAquarium(object) {
        return object.x >= this.x && object.x <= this.x + this.width && object.y >= this.y && object.y <= this.y + this.height;
    }

    addThing(thingInput) {
        // Loop through class_hierarchy backwards to find the most specific class that has a constructor
        let thingClass = Thing;
        const reversedClassHierarchy = thingInput.class_hierarchy.reverse();
        for (let class_name of reversedClassHierarchy) {
            try {
                thingClass = eval(class_name);
                break;
            } catch (e) {
                // Do nothing
            }
        }
        let thing = new thingClass(thingInput);
        const isFish = thing.class_hierarchy.includes("Fish");
        this.addChildAt(thing, isFish ? this.children.length : 0);
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
// Check /docs/classes.md for more information
class Thing extends PIXI.AnimatedSprite {
    constructor(thingInput) {

        // Create an AnimatedSprite with a single texture or an animation
        const hasTexture = thingInput.default_texture !== null;
        const hasAnimation = thingInput.default_animation !== null;
        if (!hasTexture && !hasAnimation) {
            console.log("Thing created without texture or animation");
            return;
        } else if (hasAnimation) {
            // Create a sprite with the given animation
            const animations = PIXI.Assets.get(thingInput.spritesheet_json).data.animations;
            const animation = animations[thingInput.default_animation];
            super(animation.map(frame => PIXI.Texture.from(frame)));
            // Save the list of animations for later, then play the default animation
            this.animations_list = animations;
            this.play();
        } else {
            // Create a sprite with the given texture
            super([PIXI.Assets.get(thingInput.default_texture)]);
        }

        // Wait until we've instantiated the sprite to save properties
        self.hasTexture = hasTexture;
        self.hasAnimation = hasAnimation;

        // Unpack everything from the thingInput JSON object as properties
        this.label = thingInput.label; // Or else serverUpdate will fail
        this.serverUpdate(thingInput);

        // Bind external methods :)
        this.handleTicker = this.handleTicker.bind(this);
        this.serverUpdate = this.serverUpdate.bind(this);

        // Set the anchor to the center of the sprite
        // Scaling is handled by setting height and width (properties of PIXI.Sprite)
        this.anchor.set(0.5);

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
        this.handleAnimation();
    }

    handleAnimation() {

        // Tint the fish redder if it's hungry
        if (this.hunger > 50) {
            this.tint = 0xff0000;
        } else {
            this.tint = 0xffffff;
        }

        // Choose the fish's animation based on it's state (same string)
        const animation = this.animations_list[this.state];
        if ((this.animation !== animation) && (animation !== undefined)) {
            this.textures = animation.map(frame => PIXI.Texture.from(frame));
            this.animation = animation;
        }

        // Scale the animation speed based on the fish's speed
        this.animationSpeed = 0.1 + 0.1 * this.speed / 100;
    
        // Flip the fish based on its direction
        if (this.destination_x > this.server_x) {
            this.scale.x = -Math.abs(this.scale.x);
        } else {
            this.scale.x = Math.abs(this.scale.x);
        }

        // Slightly tilt the fish up/down (no more than 10˚)
        const angle = Math.atan2(this.destination_y - this.server_y, this.destination_x - this.server_x);
        const squareComponentOfAngle = 1 - (Math.cos(angle) ** 2);
        const tilt = squareComponentOfAngle * Math.PI / 9;
        const upOrDown = Math.sin(angle) > 0 ? 1 : -1;
        const leftOrRight = Math.cos(angle) > 0 ? 1 : -1;
        this.rotation = upOrDown * tilt * leftOrRight;

        // Play the animation
        this.play();

    }
}

class Coin extends Thing {
    constructor(texture, coinInput) {
        super(texture, coinInput);

        // Higlight the coin when the mouse is over it
        this.interactive = true;
        this.buttonMode = true;
        this.on("pointerover", () => {
            this.tint = 0x00ff00;
        });
        this.on("pointerout", () => {
            this.tint = 0xffffff;
        });

        // Send a "click" event to the server when the coin is clicked
        this.on("pointerdown", () => {
            interactionsSocket.emit("click", { 
                username: userInfo.username,
                label: this.label,
                timestamp: Date.now()
            });
        });
    }

    handleTicker(ticker) {
        this.interpolatePosition(ticker.deltaTime);
    }
}


// Not really different from Thing, but it's good to explicitly define it
class Food extends Thing {
    constructor(texture, foodInput) {
        super(texture, foodInput);
    }
    
    handleTicker(ticker) {
        this.interpolatePosition(ticker.deltaTime);
    }
}

export { Aquarium };
