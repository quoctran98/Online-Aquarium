import { socket, aquariumSocket, interactionsSocket, usersSocket } from "../sockets.js";
import { Aquarium } from "../models/gameModels.js";
import { Tool } from "../models/interactionModels.js";
import { thisUser } from "../user.js";

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
await PIXI.Assets.load("assets/fish/guppy.json");
await PIXI.Assets.load("assets/shelf/shelf.png");
await PIXI.Assets.load("assets/shelf/fish_flakes.png");
await PIXI.Assets.load("assets/shelf/brush.png");

// Render the shelf 
let shelf = new PIXI.Sprite(PIXI.Assets.get("assets/shelf/shelf.png"));
shelf.scale.x = 0.5;
shelf.scale.y = 0.5;
shelf.x = 0;
shelf.y = 150;
app.stage.addChild(shelf);

// Add the fish flakes to the shelf
let fishFlakes = new Tool("assets/shelf/fish_flakes.png", thisUser);
fishFlakes.scale.x = 0.35;
fishFlakes.scale.y = 0.35;
fishFlakes.x = 100;
fishFlakes.y = 90;
fishFlakes.anchor.set(0.5);
app.stage.addChild(fishFlakes);

// Add the brush to the shelf
let brush = new Tool("assets/shelf/brush.png", thisUser);
brush.scale.x = 0.4;
brush.scale.y = 0.4;
brush.x = 400
brush.y = 120;
brush.anchor.set(0.5);
app.stage.addChild(brush);

// Draw the aquarium (load the background and make sure it's 960x540)
let background = new PIXI.Sprite(PIXI.Assets.get("assets/background.png"));
background.scale.x = 960 / background.texture.width;
background.scale.y = 540 / background.texture.height;
background.x = 0;
background.y = 200;
app.stage.addChild(background);

// Make an aquarium container :)
let aquarium = new Aquarium({x: 0, y: 200, width: 960, height: 540});
app.stage.addChild(aquarium);

// Add food to the aquarium where the user clicks
app.stage.on("click", (event) => {
  let aquariumPosition = aquarium.toLocal(event.data.global);
  interactionsSocket.emit("feed", { x: aquariumPosition.x, y: aquariumPosition.y });
  // take away 0.01 money for now (just client-side)
  thisUser.updateMoney(thisUser.money - 0.01);
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
  const newMoney = newUserInfo.money;
  thisUser.updateMoney(newMoney);
  // It's okay to not update the hidden <p> tags because that's just used for initializing thisUser
});
