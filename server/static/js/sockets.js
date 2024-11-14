import { io } from "https://cdn.socket.io/4.8.0/socket.io.esm.min.js";

const socket = io();
const usersSocket = io("/users");
const chatSocket = io("/chat");
const aquariumSocket = io("/aquarium"); 
const interactionsSocket = io("/interactions");
const storeSocket = io("/store");

socket.on("connect", () => { console.log("Connected to the server!"); });
usersSocket.on("connect", () => { console.log("Connected to the users namespace!"); });
chatSocket.on("connect", () => { console.log("Connected to the chat namespace!"); });
aquariumSocket.on("connect", () => { console.log("Connected to the aquarium namespace!"); });
interactionsSocket.on("connect", () => { console.log("Connected to the interactions namespace!"); });
storeSocket.on("connect", () => { console.log("Connected to the store namespace!"); });

export { socket, usersSocket, chatSocket, aquariumSocket, interactionsSocket, storeSocket };