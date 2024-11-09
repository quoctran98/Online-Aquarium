import { io } from "https://cdn.socket.io/4.8.0/socket.io.esm.min.js";

const socket = io();
const aquariumSocket = io("/aquarium"); 
const interactionsSocket = io("/interactions");
const chatSocket = io("/chat");

socket.on("connect", () => { console.log("Connected to the server!"); });
aquariumSocket.on("connect", () => { console.log("Connected to the aquarium namespace!"); });
interactionsSocket.on("connect", () => { console.log("Connected to the interactions namespace!"); });
chatSocket.on("connect", () => { console.log("Connected to the chat namespace!"); });

export { socket, aquariumSocket, interactionsSocket, chatSocket };