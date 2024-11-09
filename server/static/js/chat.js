import { chatSocket } from "./sockets";
import { parse_p_tags } from "./utils";

const userInfo = parse_p_tags("user-info");

chatSocket.emit("new_message", {
    username: userInfo.username,
    message: "Hello, world!",
    timestamp: Date.now()
});