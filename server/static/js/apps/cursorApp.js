import { socket, interactionsSocket } from "../sockets.js";
import { CursorContainer } from "../models/interactionModels.js";
import { parse_p_tags } from "../utils.js";

const userInfo = parse_p_tags("user-info");
console.log(userInfo);

const app = new PIXI.Application();
await app.init({ 
  resizeTo: $("#full-screen-container").get(0),
  autoDensity: true,
  backgroundColor: 0xffffff
});
app.stage.interactive = true;
$("#full-screen-container").get(0).appendChild(app.canvas);

await PIXI.Assets.load("assets/cursor.png");

// Render all other clients' cursors (in a separate container)
let cursorContainer = new CursorContainer(userInfo.username);
app.stage.addChild(cursorContainer);

// Register event listeners for the interactions socket
interactionsSocket.on("update_cursor", (data) => { 
  console.log(data);
  cursorContainer.updateCursor(data); 
});
interactionsSocket.on("user_disconnected", (username) => { cursorContainer.removeCursor(username); });

// Broadcast the client's cursor position to all other clients
app.stage.on("mousemove", (event) => {
  let position = event.data.global;
  console.log(position);
  interactionsSocket.emit("my_cursor", { 
    username: userInfo.username,
    x: position.x, 
    y: position.y, 
    event: "mousemove" 
  });
});