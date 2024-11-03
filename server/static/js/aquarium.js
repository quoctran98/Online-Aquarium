import socket from "./socket.js";

// const maxHeight = window.innerHeight * 0.9;
// const maxWidth = window.innerWidth * 0.9;

const app = new PIXI.Application();
await app.init({ width: 1280, height: 720, backgroundColor: 0xFFFFFF });
document.body.appendChild(app.canvas);

// Preload the goldfish image (we'll do this for all the fish later or use a spritesheet)
await PIXI.Assets.load("assets/fish/goldfish.png");
await PIXI.Assets.load("assets/shelf/fish_flakes.png");

// Render the shelf (just a brown rectangle) on load
let shelf = new PIXI.Graphics();
shelf.beginFill(0x8B4513);
shelf.drawRect(0, 0, app.screen.width, app.screen.height / 4);
shelf.endFill();
app.stage.addChild(shelf);
// Add the fish flakes to the shelf
let flakes = new PIXI.Sprite(PIXI.Assets.get('assets/shelf/fish_flakes.png'));
flakes.width = 100;
flakes.height = 100 * flakes.texture.height / flakes.texture.width;

flakes.x = 0;
flakes.y =  shelf.height - flakes.height;

app.stage.addChild(flakes);

// Render an aquarium
let aquarium = new PIXI.Graphics();
aquarium.beginFill(0x00FFFF);
aquarium.drawRect(0, app.screen.height / 4, 500, 500);
aquarium.endFill();
app.stage.addChild(aquarium);


// Render fish when we receive a message from the server (if it's a new fish)
let current_fish_ids = [];
function updateFishes(fishes) {
  for (let i = 0; i < fishes.length; i++) {
    let fish = fishes[i];

    if (!current_fish_ids.includes(fish.id)) {
      console.log(`Adding fish ${fish.id}`);
      current_fish_ids.push(fish.id);

      let sprite = new PIXI.Sprite(PIXI.Assets.get('assets/fish/goldfish.png'));
      sprite.label = fish.id;
      sprite.x = fish.position.x;
      sprite.y = fish.position.y;
      sprite.width = fish.length;
      sprite.height = fish.length * sprite.texture.height / sprite.texture.width;
      aquarium.addChild(sprite);

    } else{
      // just update the position of the fish
      let sprite = aquarium.getChildByLabel(fish.id);
      sprite.x = fish.position.x;
      sprite.y = fish.position.y;
      if (fish.facing == "right") {
        sprite.scale.x = Math.abs(sprite.scale.x);
      } else {
        sprite.scale.x = -Math.abs(sprite.scale.x);
      }

    }
  }
}

// send a message to the server when the user clicks
$(document).click(function() {
  socket.emit("message", "add_fish");
});

// receive a message from the server
socket.on("updateFishes", function(data) {
  updateFishes(data);
});
