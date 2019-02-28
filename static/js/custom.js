/* global $ */

$(document).ready(function() {
    // Allow the user to view the password(s) they entered
    $('.pw-show').on('click', function() {
        $('.pw-show-text').prop('type', function(i,text){
            return text === 'text' ? 'password' : 'text';
        });
        $('.pw-show-eye').text(function(i,text){
            return text === 'visibility' ? 'visibility_off' : 'visibility';
        });
    });

    // Trigger CSS changes when user adds a comic to their list
    // and trigger the POST link
    $('.addCheckbox').on('click', function() {
        var _id = $(this).attr('value');
        var comic_id =$(this).attr('name');
        $.ajax({
            url: '/add_to_list',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ '_id': _id })
        })
        .done(function(data) {
            $(`#cb-text-${comic_id}`).text('Added');
            $(`#${comic_id}`).attr('disabled', 'disabled');
            $(`#${comic_id}-card`).fadeTo(500,.5);
            $(`.flip-colour-${comic_id}`).removeClass('lighten-2').addClass('lighten-3');
        });
    });
    
    // Trigger CSS changes when user marks a comic as read
    // and trigger the POST link
    $('.markCheckbox').on('click', function() {
        var _id = $(this).attr('value');
        var comic_id = $(this).attr('name');
        $.ajax({
            url: '/mark_comic_read',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ '_id': _id })
        })
        .done(function(data) {
            $(`#cb-text-${comic_id}`).text('Marked Read');
            $(`#${comic_id}`).attr('disabled', 'disabled');
            $(`#${comic_id}-card`).fadeTo(500,.5);
            $(`.flip-colour-${comic_id}`).removeClass('lighten-2').addClass('lighten-3');
        });
    });
    
    // Trigger CSS changes when user deletes a comic from their list
    // and trigger the POST link
    $('.delCheckbox').on('click', function() {
        var _id = $(this).attr('value');
        var comic_id = $(this).attr('name');
        $.ajax({
            url: '/delete_comic',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ '_id': _id })
        })
        .done(function(data) {
            $(`#cb-text-${comic_id}`).text('Deleted From List');
            $(`#${comic_id}`).attr('disabled', 'disabled');
            $(`#${comic_id}-card`).fadeTo(500,.5);
            $(`.flip-colour-${comic_id}`).removeClass('lighten-2').addClass('lighten-3');
        });
    });
    
    // Trigger CSS changes when admin deletes a user
    // and trigger the POST link    
    $('.del-user').on('click', function() {
        var user_name = $(this).attr('name');
        $.ajax({
            url: '/adm_del_user',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'user_name': user_name })
        })
        .done(function(data) {
            $(`#del-${user_name}`).text('User Deleted');
            $(`#del-${user_name}`).attr('disabled', 'disabled');
            $(`.${user_name}-td`).fadeTo(500,.5);
            $(`.flip-colour-${user_name}`).removeClass('lighten-2').addClass('lighten-3');
        });
    });
    
});

