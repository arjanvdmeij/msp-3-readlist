/* global $  M */

$(document).ready(function(){
    $('.collapsible').collapsible();
  });

function disableButton(which,title) {
    $(which).addClass('disabled');
    M.toast({html: `${title}<br>Added To List`, 
    displayLength:1000,
    classes: 'blue-grey darken-1 white-text'});
    return;
}