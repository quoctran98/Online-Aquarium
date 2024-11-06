import { socket, aquariumSocket, interactionsSocket } from "./sockets.js";
import { Fish, Aquarium, Thing, Cursor } from "./models.js";

// const maxHeight = window.innerHeight * 0.9;
// const maxWidth = window.innerWidth * 0.9;

const app = new PIXI.Application();
await app.init({ width: 1200, height: 800, backgroundColor: 0xFFFFFF });
document.body.appendChild(app.canvas);

// Preload the goldfish image (we'll do this for all the fish later or use a spritesheet)
await PIXI.Assets.load("assets/fish/goldfish.png");
await PIXI.Assets.load("assets/shelf/fish_flakes.png");
await PIXI.Assets.load("assets/cursor.png");

// Render the shelf (just a brown rectangle) on load
let shelf = new PIXI.Graphics()
  .rect(0, 0, 500, 100)
  .fill(0x8B4513);
app.stage.addChild(shelf);

// Add the fish flakes to the shelf
let flakes = new Thing(PIXI.Assets.get("assets/shelf/fish_flakes.png"));
flakes.scale.x = 100 / flakes.texture.width;
flakes.scale.y = 100 / flakes.texture.height;
flakes.x = 0;
flakes.y =  shelf.height - flakes.height;
flakes.interactive = true;
flakes.buttonMode = true;
flakes.on("pointerdown", () => {
  interactionsSocket.emit("pick_up_item", { type: "fish_flakes" });
  flakes.on("pointermove", onDragMove);
  flakes.on("pointerup", onDragEnd);
  flakes.on("pointerupoutside", onDragEnd);
});
function onDragMove(event) {
  const newPosition = event.data.global;
  flakes.x = newPosition.x - flakes.width / 2;
  flakes.y = newPosition.y - flakes.height / 2;
}
function onDragEnd() {
  flakes.off("pointermove", onDragMove);
  flakes.off("pointerup", onDragEnd);
  flakes.off("pointerupoutside", onDragEnd);
}
app.stage.addChild(flakes);

// Draw the aquarium (do this BEFORE adding the aquarium container)
let water = new PIXI.Graphics()
  .rect(0, 100, 500, 500)
  .fill(0x00FFFF)
app.stage.addChild(water);

// Make an aquarium container :)
let aquarium = new Aquarium();
app.stage.addChild(aquarium);

// send a message to the server when the user clicks
// just for testing purposes
$(document).click(function() {
  interactionsSocket.emit("add_fish", { type: "goldfish" });
});

// Register event listeners for the aquarium socket
aquariumSocket.on("sync_fishes", aquarium.syncFishes);
aquariumSocket.on("update_fish", aquarium.updateFish);

// Broadcast the client's cursor position to all other clients
document.addEventListener("mousemove", (event) => {
  interactionsSocket.emit("my_cursor", { 
    username: socket.id,
    x: event.clientX,
    y: event.clientY,
    event: "mousemove"
  });
});

// Render all other clients' cursors (in a separate container)
let cursors = new PIXI.Container();
app.stage.addChild(cursors);

// Function to add a single cursor to the aquarium when a new one is sent by the server
function addCursor(cursor_data) {
  // Don't add if it's the current user's cursor
  if (cursor_data.username === socket.id) return;
  let cursor = new Cursor(PIXI.Assets.get("assets/cursor.png"), cursor_data);
  cursors.addChild(cursor);
}

// Function to update a single cursor when the server broadcasts an update or a sync
function updateCursor(cursor_data) {
  // Don't update if it's the current user's cursor
  if (cursor_data.username === socket.id) return;
  let cursor = cursors.children.find(c => c.label === cursor_data.username);
  if (!cursor) { // If the cursor isn't in the list, add it!
    addCursor(cursor_data); 
  }
  cursor.serverUpdate(cursor_data);
}

// // Function to remove a cursor from the aquarium
function removeCursor(cursor_id) {
  console.log(`This session's socket ID: ${socket.id}`);
  console.log(`Cursor ID to remove: ${cursor_id}`);
  console.log(`Cursors: ${cursors.children.map(c => c.label)}`);
  let cursor = cursors.children.find(c => c.label === cursor_id);
  if (cursor) {
    cursors.removeChild(cursor);
  } else {
    console.log(`Cursor ${cursor_id} not found in cursors`);
  }
}

// Register event listeners for the interactions socket
interactionsSocket.on("update_cursor", updateCursor);
interactionsSocket.on("user_disconnected", (username) => { removeCursor(username); });
