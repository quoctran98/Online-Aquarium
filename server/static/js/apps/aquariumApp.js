import { socket, aquariumSocket, interactionsSocket } from "../sockets.js";
import { Aquarium } from "../models/gameModels.js";
import { thisUser, userManager } from "../models/userModels.js";
import { Tool, CursorContainer } from "../models/interactionModels.js";
import { animateCursor } from "../utils.js";

const app = new PIXI.Application();
await app.init({ 
  resizeTo: $("#aquarium-container").get(0),
  autoDensity: true,
  backgroundColor: 0xffffff
});
app.stage.interactive = true;
app.canvas.style.position = "absolute";
app.canvas.style.top = "0";
app.canvas.style.left = "0";
app.canvas.style.zIndex = "0"; // Place on bottom!
$("#aquarium-container").get(0).appendChild(app.canvas);

// Preload the goldfish image (we'll do this for all the fish later or use a spritesheet)
await PIXI.Assets.load("assets/cursors.json");
await PIXI.Assets.load("assets/tap.json");
await PIXI.Assets.load("assets/things.json");
await PIXI.Assets.load("assets/fish/clownfish.json");
await PIXI.Assets.load("assets/fish/guppy.json");

await PIXI.Assets.load("assets/background.png");
await PIXI.Assets.load("assets/shelf/shelf.png");
await PIXI.Assets.load("assets/shelf/flake_bottle.png");
await PIXI.Assets.load("assets/shelf/pellet_bottle.png");
await PIXI.Assets.load("assets/shelf/brush.png");

// Make a big container for everything, so we can easily rescale and resize it :)
let gameContainer = new PIXI.Container();

// Make a shelf container for toolbar stuff :)
let shelfContainer = new PIXI.Container();
shelfContainer.x = 0;
shelfContainer.y = 0;
shelfContainer.width = 960;
shelfContainer.height = 200;
gameContainer.addChild(shelfContainer);

// Render the shelf
let shelfSprite = new PIXI.Sprite(PIXI.Assets.get("assets/shelf/shelf.png"));
shelfSprite.scale.x = 0.5;
shelfSprite.scale.y = 0.5;
shelfSprite.x = 0;
shelfSprite.y = 200 - 20 - shelfSprite.height;
shelfContainer.addChild(shelfSprite);

// Retrive /data/tools.json then add the tools to the stage
fetch("/data/tools.json")
  .then(response => response.json())
  .then(toolsData => {
    for (let key in toolsData) {
      const data = toolsData[key];
      let tool = new Tool(data, thisUser);
      shelfContainer.addChild(tool);
    }
});

// Draw the background (load the background and make sure it's 960x540)
let aquariumBackground = new PIXI.Sprite(PIXI.Assets.get("assets/background.png"));
aquariumBackground.scale.x = 960 / aquariumBackground.texture.width;
aquariumBackground.scale.y = 540 / aquariumBackground.texture.height;
aquariumBackground.x = 0;
aquariumBackground.y = 200;
aquariumBackground.interactive = true; // Can't click through the background
gameContainer.addChild(aquariumBackground);

// Add the actual aquarium to the aquarium container
let aquarium = new Aquarium({x: 0, y: 200, width: 960, height: 540});
gameContainer.addChild(aquarium);

// Add the aquarium container to the stage
app.stage.addChild(gameContainer);

////////////////////////////////////////
// Resize the Containers to fit the app
////////////////////////////////////////

// Assuming `app` is your PIXI Application and `container` is your PIXI Container
const resize = () => {
  const divWidth = app.view.parentElement.clientWidth; // Get the div's width
  const divHeight = app.view.parentElement.clientHeight; // Get the div's height

  const containerWidth = gameContainer.width; // Fixed container width
  const containerHeight = gameContainer.height; // Fixed container height

  // Calculate aspect ratios
  const divAspect = divWidth / divHeight;
  const containerAspect = containerWidth / containerHeight;

  // Determine scaling factor
  let scale;
  if (divAspect > containerAspect) {
      // Div is wider relative to container, scale by height
      scale = divHeight / containerHeight;
  } else {
      // Div is taller relative to container, scale by width
      scale = divWidth / containerWidth;
  }

  // Apply scale to container
  gameContainer.scale.set(scale, scale);

  // Center the container
  gameContainer.x = (divWidth - containerWidth * scale) / 2;
  gameContainer.y = 0;
};

// Attach the resize function to the window resize event
window.addEventListener('resize', () => {
  resize();
  app.renderer.resize(app.view.parentElement.clientWidth, app.view.parentElement.clientHeight);
});

// Initial call to set up the layout
resize();

//////////////////////////////
// Add socket event listeners
//////////////////////////////

// Register event listeners for the aquarium socket
aquariumSocket.on("sync_everything", aquarium.syncEverything);
aquariumSocket.on("update_thing", aquarium.updateThing);

//////////////////////////////
// Add clicking event handlers
//////////////////////////////

// Handle the user clicking on the aquarium! (for some reason this doesn't work with the aquarium container)
let lastClick = 0;
aquariumBackground.on("click", (event) => {
  console.log("Click!");
  // Prevent spam clicking (should also implement this on the server)
  if (Date.now() - lastClick < 500) { return; } // 500ms
  lastClick = Date.now();
  // Get the position of the click relative to the background (and aquarium)
  let aquariumPosition = aquarium.toLocal(event.data.global);
  let data = {
    username: thisUser.username,
    x: aquariumPosition.x,
    y: aquariumPosition.y,
  }
  // Send a tap or use event to the server
  if (thisUser.toolSelected == null) {
    interactionsSocket.emit("tap", data);
  } else {

    // Add the tool type to the data object
    const tool = thisUser.toolSelected;
    data.tool = tool.toolType;

    // Check if the user has enough money; backend will also check
    if (tool.cost <= thisUser.money) {
      thisUser.updateUserInfo({ money: Math.round(100*(thisUser.money - tool.cost))/100 });
      interactionsSocket.emit("use", data);
    }

    // Unseslect the tool if the user doesn't have enough money (because of this interaction or a previous)
    if (tool.cost > thisUser.money) {
      thisUser.deselectTool();
    }

  }
});

///////////////
// Update Users
///////////////

// Update user info on the "update_user" event
interactionsSocket.on("update_user", (newUserInfo) => {
  console.log(newUserInfo);
  if (newUserInfo.username === thisUser.username) {
    thisUser.updateUserInfo(newUserInfo);
  } else { // Update other users info.
    userManager.updateUserInfo(newUserInfo);
  }
});

///////////////////////////
// Cursor Interaction Code
///////////////////////////

// Render all other clients' cursors (in a separate container)
let cursorContainer = new CursorContainer();
gameContainer.addChild(cursorContainer);

// Broadcast the client's cursor position to all other clients
app.stage.on("mousemove", (event) => {
  let cursorPosition = cursorContainer.toLocal(event.data.global);
  interactionsSocket.emit("cursor", { 
    username: thisUser.username,
    x: cursorPosition.x, 
    y: cursorPosition.y, 
    timestamp: Date.now()
  });
});

// Recieve other clients' cursor positions
const cursorEveents = ["cursor", "tap", "pickup", "click", "use", "select"];
for (let eventName of cursorEveents) {
  interactionsSocket.on(eventName, (data) => {
    if (data.username === thisUser.username) { return; }
    cursorContainer.updateCursor(data, eventName);
  });
}

//////////////////
// Debugging stuff
//////////////////

// Broadcast all the children of Aquarium when the space bar is pressed (for debugging)
$(document).keypress(function(event) {
  if (event.which == 32) {
    console.log("Children of Aquarium:");
    for (let child of aquarium.children) {
      console.log(child);
    }
  }
});
