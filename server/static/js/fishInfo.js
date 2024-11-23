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
                <h3>${this.fish_name}</h3>
                <p>Health: ${this.health}</p>
                <p>Hunger: ${this.hunger}</p>
                <p>Happiness: ${this.happiness}</p>
            </div>
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