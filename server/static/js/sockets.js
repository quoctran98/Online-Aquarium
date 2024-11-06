import { io } from "https://cdn.socket.io/4.8.0/socket.io.esm.min.js";

const socket = io(); // For the main namespace 
const aquariumSocket = io("/aquarium");
const interactionsSocket = io("/interactions");

export { socket, aquariumSocket, interactionsSocket };