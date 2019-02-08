/* global $ */

$(document).ready(function() {
    $('.pw-show').on('click', function() {
        $('.pw-show-text').prop('type', function(i,text){
            return text === 'text' ? 'password' : 'text';
        });
        $('.pw-show-eye').text(function(i,text){
            return text === 'visibility' ? 'visibility_off' : 'visibility';
        });
    });

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
    
});

