import { changeCursor, resetCursor } from "../utils.js";
import { socket, interactionsSocket } from "../sockets.js";

// Tools are things that are on the shelf. Selecting them will change how the cursor interacts with the aquarium.
class Tool extends PIXI.Sprite {
    constructor(toolJSON, thisUser) {
        super(PIXI.Assets.get(toolJSON.textureURL));

        // Required properties
        this.textureURL = toolJSON.textureURL; // Just to keep :)
        this.toolType = toolJSON.toolType;
        this.cost = toolJSON.cost;
        this.eventMode = "static"

        // Set scale, position, and anchor
        this.scale.x = toolJSON.scale.x;
        this.scale.y = toolJSON.scale.y;
        this.x = toolJSON.x;
        this.y = toolJSON.y;
        this.anchor.set(0.5);

        // thisUser is the frontend global object that represents the user

        // Highlight the tool when the cursor is over it
        this.on("pointerover", () => {
            this.tint = 0xaaaaaa;
        });
        this.on("pointerout", () => {
            this.tint = 0xffffff;
        });

        // Select the tool when it's clicked
        this.on("pointerdown", () => {
            this.selectTool(thisUser);
         });
    }

    selectTool(user) { // User object


        // If the tool is already selected, deselect it
        if (user.toolSelected == this) {
            user.toolSelected = null;
            resetCursor();

        // Otherwise select the tool
        } else {
            user.toolSelected = this;
            // Change the cursor to the tool's image (maintain aspect ratio)
            let cursorWidth;
            let cursorHeight;
            if (this.width > this.height) {
                cursorWidth = 32;
                cursorHeight = 32 * (this.height / this.width);
            } else {
                cursorHeight = 32;
                cursorWidth = 32 * (this.width / this.height);
            }
            changeCursor("/static/"+this.textureURL, cursorWidth, cursorHeight);
        }

        // Broadcast the tool selection to the server
        interactionsSocket.emit("select", { 
            tool: user.toolSelected ? user.toolSelected.toolType : null,
            username: user.username,
            timestamp: Date.now()
        });


    }
}

// To render other players' cursors and have them do things
// (I hate how much we hardcode stuff here...)
class Cursor extends PIXI.AnimatedSprite {
    constructor(cursor_input) {

        // Load the sprite with a static texture initially
        const texture = PIXI.Assets.get("cursor_point_0.png"); // In spritesheet!
        super([texture]);

        // Keep track of who the cursor belongs to
        this.label = cursor_input.username;
        this.username = cursor_input.username;
        
        // Set anchor to the top left corner (to mimick actual cursor position)
        this.anchor.set(0, 0);
        // Set size to real cursor size -- rescaling our whole game will change it though :)
        // For some reason 64x64 fits perfectly with my actual cursor size...
        this.width = 64;
        this.height = 64;

        // // Create a label for the cursor
        // this.label = new PIXI.Text(cursor_input.username, { fontFamily: "Arial", fontSize: 12, fill: 0x000000 });
        // this.label.anchor.set(0.5);
        // this.addChild(this.label);

        // Set the cursor's initial position
        this.updateCursor(cursor_input);
    }

    playAnimation(eventName) {
        const nFrames = 4; // All animations have 4 frames for now
        let animationName;
        switch (eventName) {
            case "tap":
                animationName = "cursor_point";
                break;
            case "pickup":
                animationName = "cursor_grab";
                break;
            case "click":
                animationName = "cursor_grab";
                break;
            case "use":
                animationName = "cursor_waggle";
                break;
            case "select":
                animationName = "cursor_grab";
                break;
            default:
                animationName = null;
        }
        if (animationName) {
            let textures = [];
            for (let i = 0; i < nFrames; i++) {
                textures.push(PIXI.Assets.get(`${animationName}_${i}.png`));
            }
            this.textures = textures;
            this.animationSpeed = 0.1;
            // Play once (we'll revert back to the static texture another way -- it's hacky...)
            this.loop = false;
            this.play();
        } else {
            // Revert to the static texture
            this.textures = [PIXI.Assets.get("cursor_point_0.png")];
            this.loop = false;
            this.play();
        }
    }

    updateCursor(cursor_data, eventName) {
        if (eventName == "cursor") {
            // Workaround for the cursor jumping around when an event is triggered?
            this.x = cursor_data.x;
            this.y = cursor_data.y;
        }
        // // Move the label with the cursor
        // this.label.x = this.x + 32;
        // this.label.y = this.y + 32;
        // Play an animation if the cursor is doing something
        this.playAnimation(eventName);
    }
}

// To hold and manage all the cursors
class CursorContainer extends PIXI.Container {
    constructor() {
        super();
        
        // Bind all methods that we (might) need to call externally
        this.addCursor = this.addCursor.bind(this);
        this.updateCursor = this.updateCursor.bind(this);
        this.removeCursor = this.removeCursor.bind(this);

    }

    addCursor(cursor_data) {
        let cursor = new Cursor(cursor_data);
        this.addChild(cursor);
        return(cursor);
      }

    updateCursor(cursor_data, eventName) {
        let cursor = this.children.find(c => c.label === cursor_data.username);
        if (!cursor) { // If the cursor isn't in the list, add it!
            cursor = this.addCursor(cursor_data); 
        }
        cursor.updateCursor(cursor_data, eventName);
    }

    removeCursor(username) {
        let cursor = this.children.find(c => c.label === username);
        if (cursor) {
            this.removeChild(cursor);
        } else {
          console.log(`Cursor ${username} not found in cursors`);
        }
      }
}

export { Tool, CursorContainer };