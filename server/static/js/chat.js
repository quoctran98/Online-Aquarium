import { socket, chatSocket } from "./sockets.js";
import { thisUser } from "./models/userModels.js";

class Message {
    constructor({ username, message, timestamp }) {
        this.username = username;
        this.message = message;
        this.timestamp = timestamp;
    }
    render() {
        return `
            <div class="chat-message">
                <span class="username">${this.username}</span>
                <span class="timestamp">${new Date(this.timestamp).toLocaleTimeString()}</span>
                <p>${this.message}</p>
            </div>
        `;
    }
}

// Add an event listener for a button within #chat-form
$("#chat-form").submit(function(e) {
    e.preventDefault();
    const message = $("#chat-form input").val();
    chatSocket.emit("new_message", {
        username: thisUser.username,
        message,
        timestamp: Date.now()
    });
    $("#chat-form input").val("");
});

// Add an event listener for the "new_message" event
chatSocket.on("new_message", function(data) {
    const message = new Message(data);
    $("#chat-messages-container").append(message.render());
});

// Load a list of messages from the server
// $(document).ready(function() {
//     $.get("/messages", function(data) {
//         data.forEach(function(message) {
//             const messageObj = new Message(message);
//             $("#chat-messages").append(messageObj.render());
//         });
//     });
// });