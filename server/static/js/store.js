import { socket, storeSocket } from './sockets.js';
import { thisUser } from './user.js';

let firstStoreLoad = false;

class StoreItem {
    constructor({ label, item_name, description, price, image_file, money_raised }) {
        this.label = label;
        this.item_name = item_name;
        this.description = description;
        this.price = price;
        this.image_file = image_file;
        this.money_raised = money_raised;
    }
    render() {
        return `
            <div class="store-item" id="${this.label}">
                <img src="${this.image_file}" style="max-width: 80%; max-height: 100px;">
                <h3>${this.item_name}</h3>
                <p>${this.description}</p>
                <p>${this.price}</p>
                <p>${this.money_raised}</p>
                <button class="contribute-button" id="contribute:${this.label}">Contribute</button>
            </div>
        `;
    }
}

// Attach an event listener to all .contribute-button elements
$(document).on("click", ".contribute-button", function(event) {
    const contributionAmount = 0.01; // This is a placeholder for now
    const label = event.target.id.split(":")[1];
    storeSocket.emit("contribute", 
        { label: label, username: thisUser.username, amount: contributionAmount }
    );
    thisUser.updateMoney(thisUser.money - contributionAmount);
});

// This really should be an HTTP request, not a socket request
storeSocket.on("summarize_store", function(data) {
    console.log(data);
    firstStoreLoad = true;
    $("#store-container").empty();
    data.forEach(function(item) {
        const storeItem = new StoreItem(item);
        $("#store-container").append(storeItem.render());
    });
});

storeSocket.on("update_item"), function(data) {
    console.log(data);
    // replace the old item with the new item if it exists
    // if ($("#" + data.label).length) {
    //     $("#" + data.label).replaceWith(new StoreItem(data).render());
    // } else {
    //     const storeItem = new StoreItem(data);
    //     $("#store-container").append(storeItem.render());
    // }
};

// I worry about timings, so this will fix it, I think :)
$(document).ready(function() {
    if (!firstStoreLoad) {
        storeSocket.emit("get_store");
    }
});
