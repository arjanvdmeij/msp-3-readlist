/* global $  M */

$(document).ready(function(){
    $('.collapsible').collapsible();
  });

function addToList(which,id,title) {
    $(which).addClass('disabled');
    M.toast({html: `Adding:<br><strong>${title}</strong>`, 
    displayLength:2000,
    classes: 'blue-grey lighten-5 blue-grey-text'});
    $(`#${id}`).html(`<i class="material-icons left">check_circle_outline</i>Added`);
    return;
}

function markAsRead(title) {
    M.toast({html: `Marking as read:<br><strong>${title}</strong>`, 
    displayLength:2000,
    classes: 'blue-grey lighten-5 blue-grey-text'});
    return;
}

function removeFromList(title) {
    M.toast({html: `Deleting:<br><strong>${title}</strong>`, 
    displayLength:2000,
    classes: 'blue-grey lighten-5 blue-grey-text'});
    return;
}