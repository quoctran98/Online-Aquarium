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

// Parse strings representations to arrays and arrays of arrays
// ChatGPT wrote this...
function parse_string_arrays(input_string) {
        // Handle the special cases of empty arrays
        if (input_string === '') {
            return([[]]) // Returning only [] makes it undefined for some reason??
        } else if (input_string === '[]') {
            return([[]]);
        }

        // Check if the input is a single tuple or an array of tuples
        const isArray = input_string.startsWith('[');
    
        // Step 1: Remove the outer brackets if it's an array
        const cleanedString = isArray ? input_string.replace(/[\[\]]/g, '') : input_string;
    
        // Step 2: Split the string by the closing parenthesis followed by a comma if it's an array
        const tuplesArray = isArray 
            ? cleanedString.split(/\),\s*\(/).map(tuple => tuple.trim())
            : [cleanedString]; // If it's a single tuple, wrap it in an array
    
        // Step 3: Convert each tuple string into an array of numbers
        return tuplesArray.map(tuple => {
            // Remove parentheses and single quotes
            const cleanedTuple = tuple.replace(/[()']/g, '');
            // Split by comma and convert to numbers
            return cleanedTuple.split(',').map(Number);
        });
}
