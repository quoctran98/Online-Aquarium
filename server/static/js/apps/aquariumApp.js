import { socket, aquariumSocket, interactionsSocket } from "../sockets.js";
import { Aquarium } from "../models/gameModels.js";
import { parse_p_tags } from "../utils.js";

const userInfo = parse_p_tags("user-info");

const app = new PIXI.Application();
await app.init({ 
  resizeTo: $("#aquarium-container").get(0),
  autoDensity: true,
  backgroundColor: 0xffffff
});
app.stage.interactive = true;
$("#aquarium-container").get(0).appendChild(app.canvas);

// Preload the goldfish image (we'll do this for all the fish later or use a spritesheet)
await PIXI.Assets.load("assets/background.png");
await PIXI.Assets.load("assets/things.json");
await PIXI.Assets.load("assets/fish/clownfish.json");
await PIXI.Assets.load("assets/shelf/fish_flakes.png");

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

// Draw the aquarium (load the background and make sure it's 960x540)
let background = new PIXI.Sprite(PIXI.Assets.get("assets/background.png"));
background.scale.x = 960 / background.texture.width;
background.scale.y = 540 / background.texture.height;
background.x = 0;
background.y = 100;
app.stage.addChild(background);

// Make an aquarium container :)
let aquarium = new Aquarium();
app.stage.addChild(aquarium);

// Add food to the aquarium where the user clicks
app.stage.on("click", (event) => {
  let aquariumPosition = aquarium.toLocal(event.data.global);
  interactionsSocket.emit("feed", { x: aquariumPosition.x, y: aquariumPosition.y });
});

// Register event listeners for the aquarium socket
aquariumSocket.on("sync_everything", aquarium.syncEverything);
aquariumSocket.on("update_thing", aquarium.updateThing);

// Broadcast all the children of Aquarium when the space bar is pressed (for debugging)
$(document).keypress(function(event) {
  if (event.which == 32) {
    console.log("Children of Aquarium:");
    for (let child of aquarium.children) {
      console.log(child);
    }
  }
});

// Update user info on the "update_user" event
interactionsSocket.on("update_user", (newUserInfo) => {
  if (newUserInfo.username == userInfo.username) {
    $(".user-money").text(`$${newUserInfo.money}`);
    // Update <p> tags in "user-info" (ids are the same as the keys in the user object)
    const hiddenUserInfo = $("#user-info");
    for (let key in newUserInfo) {
      hiddenUserInfo.find(`#${key}`).text(newUserInfo[key]);
    }
  }
});
