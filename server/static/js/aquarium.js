import { socket, aquariumSocket, interactionsSocket } from "./sockets.js";
import { Aquarium, Thing, Fish, Coin, CursorContainer } from "./models.js";

// From https://coderevue.net/posts/scale-to-fit-screen-pixijs/

const app = new PIXI.Application();
await app.init({ 
  resizeTo: $("#aquarium-container").get(0),
  autoDensity: true,
  backgroundColor: 0xffffff
});
app.stage.interactive = true;
$("#aquarium-container").get(0).appendChild(app.canvas);
console.log(app.screen.width, app.screen.height);

// Preload the goldfish image (we'll do this for all the fish later or use a spritesheet)
await PIXI.Assets.load("assets/placeholders/nothing.png");
await PIXI.Assets.load("assets/placeholders/fish.png");
await PIXI.Assets.load("assets/fish/goldfish.png");
await PIXI.Assets.load("assets/fish/guppy.png");
await PIXI.Assets.load("assets/shelf/fish_flakes.png");
await PIXI.Assets.load("assets/cursor.png");
await PIXI.Assets.load("assets/coin.png");
await PIXI.Assets.load("assets/pellet.png");

// Render the shelf (just a brown rectangle) on load
let shelf = new PIXI.Graphics()
  .rect(0, 0, app.screen.width, 100)
  .fill(0x8B4513);
app.stage.addChild(shelf);

// Add the fish flakes to the shelf
let flakes = new PIXI.Sprite(PIXI.Assets.get("assets/shelf/fish_flakes.png"));
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
  .rect(0, 100, 800, 600)
  .fill(0x00FFFF)
app.stage.addChild(water);

// Make an aquarium container :)
let aquarium = new Aquarium();
app.stage.addChild(aquarium);

// send a message to the server when the user clicks
// just for testing purposes
$(document).click(function(e) {
  const relativeX = e.pageX - $("#aquarium-container").offset().left;
  const relativeY = e.pageY - $("#aquarium-container").offset().top;
  console.log(`Clicked at (${relativeX}, ${relativeY})`);
  interactionsSocket.emit("add_food", { x: relativeX, y: relativeY });
});

// Register event listeners for the aquarium socket
aquariumSocket.on("sync_everything", aquarium.syncEverything);
aquariumSocket.on("update_thing", aquarium.updateThing);

// Render all other clients' cursors (in a separate container)
let cursorContainer = new CursorContainer(socket.id);
app.stage.addChild(cursorContainer);

// Register event listeners for the interactions socket
interactionsSocket.on("update_cursor", cursorContainer.updateCursor);
interactionsSocket.on("user_disconnected", (username) => { cursorContainer.removeCursor(username); });

// Broadcast the client's cursor position to all other clients
app.stage.on("mousemove", (event) => {
  let position = event.data.global;
  interactionsSocket.emit("my_cursor", { username: socket.id, x: position.x, y: position.y, event: "mousemove" });
});

// Broadcast all the children of Aquarium when the space bar is pressed (for debugging)
$(document).keypress(function(event) {
  if (event.which == 32) {
    console.log("Children of Aquarium:");
    for (let child of aquarium.children) {
      console.log(child);
    }
  }
});
