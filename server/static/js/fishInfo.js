import { socket, aquariumSocket } from "./sockets.js";

class FishInfo {
    constructor(fishInfo) {
        this.fish_name = fishInfo.fish_name;
        this.health = fishInfo.health;
        this.hunger = fishInfo.hunger;
        this.happiness = fishInfo.happiness;
    }

    render() {
        return `
            <div class="fish-info">
                <h4>${this.fish_name}</h4>
                <p>❤️ ${this.renderHealthBar()}</p>
                <p>🍖 ${this.renderHungerBar()}</p>
                <p>🥳 ${this.renderHappinessBar()}</p>
            </div>
        `;
    }

    renderHealthBar() {
        return `
            <meter value="${this.health}" min="0" max="1" color="red"></meter>
        `;
    }

    renderHungerBar() {
        // Make sure the hunger is inverted
        return `
            <meter value="${1-this.hunger}" min="0" max="1" color="green"></meter>
        `;
    }

    renderHappinessBar() {
        return `
            <meter value="${this.happiness}" min="0" max="1" color="yellow"></meter>
        `;
    }
}

// Add a listener for the "sync_everything" event
aquariumSocket.on("sync_everything", (listOfFish) => {
    // Clear the fish list
    $("#fish-info-container").empty();
    // Add each fish to the list
    listOfFish.forEach((fishInfo) => {
        // Make sure "Fish" is in the class hierarchy
        if (fishInfo.class_hierarchy.includes("Fish")) {
            const fish = new FishInfo(fishInfo);
            $("#fish-info-container").append(fish.render());
        }
    });
});