import { socket, chatSocket } from "./sockets.js";
import { parse_p_tags } from "./utils.js";

const userInfo = parse_p_tags("user-info");

class Message {
    constructor({ username, message, timestamp }) {
        this.username = username;
        this.message = message;
        this.timestamp = timestamp;
    }
    render() {
        return `
            <div class="message">
                <span class="username">${this.username}</span>
                <span class="timestamp">${new Date(this.timestamp).toLocaleTimeString()}</span>
                <p class="message">${this.message}</p>
            </div>
        `;
    }
}

// Add an event listener for a button within #chat-form
$("#chat-form").submit(function(e) {
    e.preventDefault();
    const message = $("#chat-form input").val();
    chatSocket.emit("new_message", {
        username: userInfo.username,
        message,
        timestamp: Date.now()
    });
    $("#chat-form input").val("");
});

// Add an event listener for the "new_message" event
chatSocket.on("new_message", function(data) {
    const message = new Message(data);
    $("#chat-messages").append(message.render());
});