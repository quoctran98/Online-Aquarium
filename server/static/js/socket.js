// socket.js
const socket = io(); // defaults to the current host, I think
socket.on("connect", function() {
    console.log("Connected to the server!");
});
socket.on("disconnect", function() {
    console.log("Disconnected from the server :(");
});
export default socket;