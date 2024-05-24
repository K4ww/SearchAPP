const { GEOMETRY } = require("mysql/lib/protocol/constants/types");

// Initialize the index of the currently hovered item to -1
var currentItemIndex = -1;

document.addEventListener('keydown', function(event) {
  // If the down arrow key is pressed
  if (event.keyCode === 40) {
    // Get the document list element
    var documentList = document.getElementById('document-list');
    // Get all the list items
    var listItems = documentList.children;
    // Remove the "hover" class from the previously hovered item
    if (currentItemIndex >= 0) {
      listItems[currentItemIndex].classList.remove('hover');
    }
    // Increment the index of the currently hovered item
    currentItemIndex++;
    // If the end of the list is reached, reset the index to 0
    if (currentItemIndex >= listItems.length) {
      currentItemIndex = 0;
    }
    // Add the "hover" class to the currently hovered item
    listItems[currentItemIndex].classList.add('hover');
  }
  // If the enter key is pressed
  else if (event.keyCode === 13) {
    // Get the document list element
    var documentList = document.getElementById('document-list');
    // Get the currently hovered item
    var hoveredItem = documentList.querySelector('.hover a');
    if (hoveredItem) {
      // Redirect to the URL of the hovered item
      window.location.href = hoveredItem.href;
    }
  }
});
