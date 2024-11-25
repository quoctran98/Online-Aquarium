import { socket, storeSocket } from './sockets.js';
import { thisUser } from './models/userModels.js';

let firstStoreLoad = false;

class StoreItem {
    constructor({ label, item_name, description, price, stock, image_file, money_raised }) {
        this.label = label;
        this.item_name = item_name;
        this.description = description;
        this.price = price;
        this.stock = stock
        this.image_file = image_file;
        this.money_raised = money_raised;
    }
    render() {
        const maxContribution = Math.min(this.price - this.money_raised, thisUser.money);
        return `
            <div class="store-item" id="${this.label}">
                <h3>${this.item_name}</h3>
                <img src="${this.image_file}">
                <p>${this.money_raised} of ${this.price} raised! (${this.stock} left)</p>
                <input type="number" id="contribute-amount_${this.label}" value="0.01" step="0.01" min="0.01" max="${maxContribution}">
                <button class="contribute-button" id="contribute_${this.label}">Contribute</button>
            </div>
        `;
    }
}

// Attach an event listener to all .contribute-button elements
$(document).on("click", ".contribute-button", function(event) {
    const label = event.target.id.split("_")[1];
    const contributionAmount = parseFloat($(`#contribute-amount_${label}`).val());
    storeSocket.emit("contribute", 
        { label: label, username: thisUser.username, amount: contributionAmount }
    );
    thisUser.updateUserInfo({ money: thisUser.money - contributionAmount });
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
