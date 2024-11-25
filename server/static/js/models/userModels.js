import { socket, usersSocket } from "../sockets.js";
import { parse_p_tags, resetCursor } from "../utils.js";

const userInfo = parse_p_tags("user-info"); // Static user info from the server

class User {
    constructor(userInfo) {
        this.username = userInfo.username;
        this.money = userInfo.money;
        this.toolSelected = null;
        this.cursor_x = null;
        this.cursor_y = null;
    }

    // Redundant method (all that changes is the money for now)
    updateUserInfo(newUserInfo) {
        this.username = newUserInfo.username;
        this.money = newUserInfo.money;
    }

    changeTool(tool) {
        this.toolSelected = tool;
    }

}

class ThisUser extends User {
    constructor(userInfo) {
        super(userInfo);
    }

    // Overwrite the updateUserInfo method to update the user's money
    updateUserInfo(newUserInfo) {
        // Update all properties that are sent
        for (let key in newUserInfo) {
            this[key] = newUserInfo[key];
        }
        // Round the money to two decimal places
        this.money = Math.round(this.money * 100) / 100;
        // Update all elements that display the user's money (.user-money)
        $(".user-money").text(this.money);
    }

    // Overwrite the changeTool method to update the user's toolSelected
    // changeTool(tool) { // Tool object or null
    //     let newToolSelected = tool.selectTool(this); // Give the tool the user object
    //     // Probably redundant but good just in case :)
    //     this.toolSelected = newToolSelected ? tool : null;
    // }

    deselectTool() {
        this.toolSelected = null;
        resetCursor();
    }

}

// To dynamically add and remove other users as they connect and disconnect
class UserManager {
    constructor() {
        this.users = {};
    }

    userConnected(userInfo) {
        this.users[userInfo.username] = new User(userInfo);
    }

    userDisconnected(username) {
        delete this.users[username];
    }

    updateUserInfo(userInfo) {
        if (this.users[userInfo.username]) {
            this.users[userInfo.username].updateUserInfo(userInfo);
        } else {
            this.users[userInfo.username] = new User(userInfo);
        }
    }

    updateCursor(cursorData) {
        if (this.users[cursorData.username]) {
            this.users[cursorData.username].cursor = cursorData;
        }
        // What if the user doesn't exist?
    }

    changeTool(username, tool) {
        if (this.users[username]) {
            this.users[username].tool_selected = tool;
        }
    }
}

let thisUser = new ThisUser(userInfo);
let userManager = new UserManager();

export { thisUser, userManager };
