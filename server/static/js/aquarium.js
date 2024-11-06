import { socket, aquariumSocket, interactionsSocket } from "./sockets.js";
import { Fish, Thing, Cursor } from "./models.js";

// const maxHeight = window.innerHeight * 0.9;
// const maxWidth = window.innerWidth * 0.9;

const app = new PIXI.Application();
await app.init({ width: 1280, height: 720, backgroundColor: 0xFFFFFF });
document.body.appendChild(app.canvas);

// Preload the goldfish image (we'll do this for all the fish later or use a spritesheet)
await PIXI.Assets.load("assets/fish/goldfish.png");
await PIXI.Assets.load("assets/shelf/fish_flakes.png");
await PIXI.Assets.load("assets/cursor.png");

// Render the shelf (just a brown rectangle) on load
let shelf = new PIXI.Graphics()
  .rect(0, 0, 500, app.screen.height / 4)
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
  .rect(0, app.screen.height / 4, 500, 500)
  .fill(0x00FFFF)
app.stage.addChild(water);

// Make an aquarium container and draw it on the screen
let aquarium = new PIXI.Container();
aquarium.x = 0;
aquarium.y = shelf.height;
aquarium.width = app.screen.width;
aquarium.height = app.screen.height - shelf.height;
app.stage.addChild(aquarium);

// Add a ticker to the aquarium to handle fish movement
aquarium.ticker = new PIXI.Ticker();
aquarium.ticker.start();

// Function to sync all the fishes when the server broadcasts an update
function syncFishes(fishes) {
  console.log("Syncing fishes...");
  const current_fish_ids = aquarium.children.map(f => f.label);
  const server_fish_ids = fishes.map(f => f.id);
  // Remove fish that are no longer in the server's list
  for (let fish_id of current_fish_ids) {
    if (!server_fish_ids.includes(fish_id)) {
      removeFish(fish_id);
    }
  }
  // Add new fish / update existing fish
  for (let fish_data of fishes) {
    updateFish(fish_data); // This function will add the fish if it doesn't exist
  }
}

// Function to add a single fish to the aquarium when a new one is sent by the server
function addFish(fish_data) {
  const fish_type = fish_data.type;
  let fish = new Fish(PIXI.Assets.get(`assets/fish/${fish_type}.png`), fish_data);
  aquarium.addChild(fish);
  aquarium.ticker.add(fish.handleTicker);
}

// Function to update a single fish when the server broadcasts an update or a sync
function updateFish(fish_data) {
  let fish = aquarium.children.find(f => f.label === fish_data.id);
  if (fish) {
    fish.serverUpdate(fish_data);
  } else {
    addFish(fish_data); // If the fish isn't in the list, add it!
  }
}

// Function to remove a fish from the aquarium
function removeFish(fish_id) {
  let fish = aquarium.children.find(f => f.label === fish_id);
  if (fish) {
    aquarium.removeChild(fish);
  } else {
    console.log(`Fish ${fish_id} not found in aquarium`);
  }
}

// send a message to the server when the user clicks
$(document).click(function() {
  interactionsSocket.emit("add_fish", { type: "goldfish" });
  // keep this on the global namespace for now -- it's just for testing
});

// Register event listeners for the aquarium socket
socket.on("sync_fishes", syncFishes);
socket.on("update_fish", updateFish);

// Broadcast the client's cursor position to all other clients
document.addEventListener("mousemove", (event) => {
  socket.emit("my_cursor", { 
    username: socket.id,
    x: event.clientX,
    y: event.clientY
  });
});
// Render all other clients' cursors (in a separate container)
let cursors = new PIXI.Container();
app.stage.addChild(cursors);

// Function to sync the positions of all other clients' cursors
// we don't need to use this if we just update one cursor at a time as they move
// function syncCursors(cursor_positions) {
//   const current_cursor_ids = cursors.children.map(c => c.label);
//   const server_cursor_ids = cursor_positions.map(c => c.username);
//   // Remove cursors that are no longer in the server's list
//   for (let cursor_id of current_cursor_ids) {
//     if (!server_cursor_ids.includes(cursor_id)) {
//       removeCursor(cursor_id);
//     }
//   }
//   // Add new cursors / update existing cursors
//   for (let cursor_data of cursor_positions) {
//     updateCursor(cursor_data); // This function will add the cursor if it doesn't exist
//   }
// }

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
  if (cursor) {
    cursor.serverUpdate(cursor_data);
  } else {
    addCursor(cursor_data); // If the cursor isn't in the list, add it!
  }
}

// // Function to remove a cursor from the aquarium
// function removeCursor(cursor_id) {
//   let cursor = cursors.children.find(c => c.label === cursor_id);
//   if (cursor) {
//     cursors.removeChild(cursor);
//   } else {
//     console.log(`Cursor ${cursor_id} not found in cursors`);
//   }
// }

// Register event listeners for the interactions socket
// socket.on("sync_cursors", syncCursors);
socket.on("update_cursor", updateCursor);
