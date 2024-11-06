import { io } from "https://cdn.socket.io/4.8.0/socket.io.esm.min.js";

const socket = io();
const aquariumSocket = io("/aquarium"); 
const interactionsSocket = io("/interactions");

socket.on("connect", () => { console.log("Connected to the server!"); });
aquariumSocket.on("connect", () => { console.log("Connected to the aquarium namespace!"); });
interactionsSocket.on("connect", () => { console.log("Connected to the interactions namespace!"); });

export { socket, aquariumSocket, interactionsSocket };