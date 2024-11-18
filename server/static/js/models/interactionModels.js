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

// Cursors are other players' cursors (will also show them picking up items)
class Cursor extends PIXI.Sprite {
    constructor(texture, cursor_input) {
        super(texture);
        this.label = cursor_input.username;
        this.username = cursor_input.username;
        this.scale.x = 30 / this.texture.width;
        this.scale.y = 30 / this.texture.height;
        this.anchor.set(0.5);
    }
}

// CursorContainer is a container for all other players' cursors (this is very similar to the Aquarium class)
class CursorContainer extends PIXI.Container {
    constructor() {
        super();
        
        this.interactive = true;

        // Bind all methods that we (might) need to call externally
        this.addCursor = this.addCursor.bind(this);
        this.updateCursor = this.updateCursor.bind(this);
        this.removeCursor = this.removeCursor.bind(this);

    }

    addCursor(cursor_data) {
        let cursor = new Cursor(PIXI.Assets.get("assets/cursor.png"), cursor_data);
        this.addChild(cursor);
        return(cursor);
      }

    updateCursor(cursor_data) {
        let cursor = this.children.find(c => c.label === cursor_data.username);
        if (!cursor) { // If the cursor isn't in the list, add it!
            cursor = this.addCursor(cursor_data); 
        }
        cursor.x = cursor_data.x;
        cursor.y = cursor_data.y;
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