// script.js

document.addEventListener('DOMContentLoaded', function() {
    var toggleButton = document.getElementById('toggle');
    var menu = document.querySelector('.menu');

    toggleButton.addEventListener('click', function() {
        menu.classList.toggle('show');
    });

    document.addEventListener('click', function(event) {
        if (!menu.contains(event.target) && !toggleButton.contains(event.target)) {
            menu.classList.remove('show');
        }
    });
});

// Detect new content added
function scrollChatToBottom() {
    var chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}
// Call the scroll function after the page has loaded
document.addEventListener('DOMContentLoaded', function() {
    scrollChatToBottom();
});


// Todo - this didnt work but would be nice to enable user enter on keyboard and send message
//instead of clicking on send button

// /**
//  * This function is a listener on chat box input at the bottom to let the users
//  * click enter button to sent their message/submit their message
//  */
// document.addEventListener('DOMContentLoaded', function() {
//     // Get the form element
//     var form = document.getElementById('chat-form');

//     // Add event listener for keydown event
//     form.addEventListener('submit', function(event) {
//         event.preventDefault(); // Prevent the default form submission
//         // Add your code to handle the form submission here
//     });
// });


/**
 * event listener to click on items and show history
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get all top-level li elements
    var topLevelItems = document.querySelectorAll('#history-list > li');
    console.log(topLevelItems)
    // Add click event listener to each top-level li
    topLevelItems.forEach(function(item) {
      item.addEventListener('click', function() {
        this.classList.toggle('open');
      });
    });
  });



/** Expansion panel for user history 
 *Add event listeners to panel items
 */
var panelItems = document.querySelectorAll('.panel-item');
panelItems.forEach(function(panelItem) {
  panelItem.addEventListener('click', function() {
    this.classList.toggle('open');
  });
});
