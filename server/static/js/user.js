import { socket, usersSocket } from "./sockets.js";
import { parse_p_tags } from "./utils.js";

const userInfo = parse_p_tags("user-info"); // Static user info from the server

class User {
    constructor(userInfo) {
        this.username = userInfo.username;
        this.money = userInfo.money;
        this.tool_selected = null;
    }

    updateMoney(money) {
        this.money = money;

        // Update all elements that display the user's money (.user-money)
        $(".user-money").text(this.money);
    }

    // Redundant method (all that changes is the money for now)
    updateUserInfo(newUserInfo) {
        this.username = newUserInfo.username;
        this.user_id = newUserInfo.user_id;
        this.money = newUserInfo.money;
    }

}

let thisUser = new User(userInfo);

export { thisUser };
