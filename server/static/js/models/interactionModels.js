import { changeCursor, resetCursor } from "../utils.js";

// Tools are things that are on the shelf. Selecting them will change how the cursor interacts with the aquarium.
class Tool extends PIXI.Sprite {
    constructor(textureURL, thisUser) {
        super(PIXI.Assets.get(textureURL));
        this.textureURL = textureURL;
        this.eventMode = "static"

        // Highlight the tool when the cursor is over it
        this.on("pointerover", () => {
            this.tint = 0xaaaaaa;
        });
        this.on("pointerout", () => {
            this.tint = 0xffffff;
        });

        // Select the tool when it's clicked
        this.on("pointerdown", () => {

            // If the tool is already selected, deselect it
            if (thisUser.tool_selected == this) {
                // Deselect the tool
                thisUser.tool_selected = null;
                resetCursor();
                return;
            }

            // Select the tool
            thisUser.tool_selected = this;
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
        });
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
        this.username = username; // So we know which cursors NOT to render (for now)

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
        let cursor = this.children.find(c => c.label === username);
        if (cursor) {
            this.removeChild(cursor);
        } else {
          console.log(`Cursor ${username} not found in cursors`);
        }
      }
}

export { Tool, CursorContainer };