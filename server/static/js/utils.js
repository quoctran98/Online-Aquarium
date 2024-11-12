/*
    This script is called in every page of the website.
    Use it to define functions that are used in multiple pages.
*/

// Format a number with commas
function format_big_number(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Set many attributes of an element at once
function set_many_attributes(element, attributes) {
    for (let key in attributes) {
        element.setAttribute(key, attributes[key]);
    }
    // No need to return anything, the element is modified in place :)
}

// Call blur_background() when any modals are opened
function blur_background() {
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

// Call unblur_background() when any modals are closed
function unblur_background() {
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

export { format_big_number, set_many_attributes, blur_background, unblur_background, parse_p_tags };
