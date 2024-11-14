/*
    This script is called in every page of the website.
    Use it to define functions that are used in multiple pages.
*/

// Format a number with commas
function formatBigNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Set many attributes of an element at once
function setManyAttributes(element, attributes) {
    for (let key in attributes) {
        element.setAttribute(key, attributes[key]);
    }
    // No need to return anything, the element is modified in place :)
}

// Call blurBackground() when any modals are opened
function blurBackground() {
    let to_blur = $(".gets-blurred");
    for (let i = 0; i < to_blur.length; i++) {
        to_blur[i].style = `
            -webkit-filter: blur(5px);
            -moz-filter: blur(5px);
            -o-filter: blur(5x);
            -ms-filter: blur(5px);
            filter: blur(5px);
        `;
    }
}

// Call unblurBackground() when any modals are closed
function unblurBackground() {
    let to_unblur = $(".gets-blurred");
    for (let i = 0; i < to_unblur.length; i++) {
        to_unblur[i].style = `
            -webkit-filter: blur(0px);
            -moz-filter: blur(0px);
            -o-filter: blur(0px);
            -ms-filter: blur(0px);
            filter: blur(0px);
        `;
    }
}

// Parse a group of <p> tags in a <div> tag into a dictionary (JS object I guess?)
function parse_p_tags(div_id) {
    let p_tags = $(`#${div_id}`).children("p");
    let parsed = {};
    for (let i = 0; i < p_tags.length; i++) {
        let p = p_tags[i];
        parsed[p.id] = p.innerText;
    }
    return(parsed);
}

// Replace the default cursor with a custom image (and resize it so it fits)
function changeCursor(imageURL, width = 32, height = 32, x = 0, y = 0, fallback = "default") {
    const img = new Image();
    img.src = imageURL;
    img.crossOrigin = "anonymous";

    img.onload = function() {
        // Create a canvas element to draw the resized image
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);
        // Get the data URL of the resized image
        const resizedImageURL = canvas.toDataURL();

        // Create or get the <style> element in the <head> tag
        let styleElement = $("#sitewide-cursor-style")[0];
        if (!styleElement) {
            styleElement = document.createElement("style");
            styleElement.id = "sitewide-cursor-style";
            document.head.appendChild(styleElement);
        }

        // Apply the cursor style to all elements
        styleElement.textContent = `* { cursor: url('${resizedImageURL}') ${x} ${y}, ${fallback}; }`;
    };
    img.onerror = function() {
        console.error("Image failed to load. Check the URL or try another image.");
    };
}

// Change the cursor back to the default
function resetCursor() {
    let styleElement = $("#sitewide-cursor-style")[0];
    if (styleElement) {
        styleElement.textContent = "";
    }
}

export { formatBigNumber, setManyAttributes, blurBackground, unblurBackground, parse_p_tags, changeCursor, resetCursor };
