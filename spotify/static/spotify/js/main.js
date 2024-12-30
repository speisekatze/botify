function delete_from_playlist(event) {
    track_uri = event.currentTarget.getAttribute('uri');
    console.info(track_uri);
    playlist_uri = $('#current_playlist_uri').attr('value');
    $.getJSON('delete_track_from_playlist/'+playlist_uri+'/'+track_uri, function(data, status) {
        event.currentTarget.closest('li').remove();
        $.getJSON('loadplaylist/'+playlist_uri, load_playlist);
    });
    event.stopPropagation();
    return true;
}

function load_playlist(data, status) {
    pl_info = data['playlist'];
    $('#playlist_name').text(pl_info['name']);
    /*$('#playlist_desc').text(pl_info['description']);*/
    $('#playlist_count').text(pl_info['trackcount']);
    $('#current_playlist_uri').val(pl_info['uri']);
    $('#playlist_img').attr('src', pl_info['image']);
    tracks = data['tracks'];
    $('ol#playlist').empty();
    tracks.forEach((track) => {
        let artists = track['artists'];
        let artist_string = "";
        artists.forEach((element, key, arr) => {
            artist_string += element['name'];
            if (key+1 < arr.length) { artist_string += ", "};
        });
        $('ol#playlist')
        .append(
            $("<li>").attr('id',track['uri'])
            .append(
                $('<img/>').addClass('icon_left delete').attr('src', 'static/spotify/img/trash.svg').attr('id', 'delete_track_from_pl').attr('uri', track['uri']).on('click', delete_from_playlist)
            )
            .append(
                $('<span>').addClass('track')
                .append(
                    $('<span>').addClass('maybelong song')
                    .append(
                        $('<span>').text(track['name'])
                    )
                )
                .append(
                    $('<span>').addClass('maybelong artist')
                    .append(
                        $('<span>').text(artist_string)
                    )
                )
            )
            .append(
                $('<img/>').addClass('cover_vsmall').attr('src', track['image'])
            )
        );
    });
    $('#waitContainer').hide();
}

function delete_artist_from_playlist(event) {
    $(event.currentTarget).parent().remove();
}

function find_related_artists(event) {
    uri = event.currentTarget.getAttribute('uri');
    $('#waitContainer').show();
    $.getJSON('relatedartists/'+uri, function(data, status) {
        artists = data['artists'];
        $('div#related_artist').empty();
        artists.forEach( artist => {
            $('div#related_artist')
            .append(
                $('<div>').addClass('artist').attr('id', artist['uri']).on('click', add_to_playlist_artists)
                .append(
                    $('<img/>').attr('src', artist['image']).attr('alt','Artist')
                )
                .append(
                    $('<span>').text(artist['name'])
                )
            );
        });
        $('#waitContainer').hide();
    });
    
}

function add_artist(artist_uri, artist_img, artist_name) {
    artist_list = $('#playlist_artist').children('div');
    for(var i = 0; i < artist_list.length; i++) {
        if (artist_list[i].id == artist_uri) {
            return false;
        }
    }
    console.info(artist_img, artist_name);
    $('div#playlist_artist')
    .append(
        $('<div>').addClass('artist').attr('id', artist_uri).on('click', add_to_playlist_artists)
        .append(
            $('<img/>').attr('src', artist_img).attr('alt','Artist')
        )
        .append(
            $('<span>').text(artist_name)
        )
        .append(
            $('<img/>').addClass('icon_right link').attr('src', 'static/spotify/img/link.svg').attr('id', 'related_artists').attr('uri', artist_uri).on('click', find_related_artists)
        )
        .append(
            $('<img/>').addClass('icon_right delete').attr('src', 'static/spotify/img/trash.svg').attr('id', 'delete_track_from_pl').attr('uri', artist_uri).on('click', delete_artist_from_playlist)
        )
    );
}

function add_to_playlist_artists(event) {
    artist_uri = event.currentTarget.closest('div').id;
    artist_img = $(event.currentTarget).children('img').attr('src');
    artist_name = $(event.currentTarget).children('span').text();
    add_artist(artist_uri, artist_img, artist_name);

}

function lookup_artist_callback(result) {
    artists = result['artists'];
    $('div#lookup_artist_list').empty();
    artists.forEach( artist => {
        $('div#lookup_artist_list')
        .append(
            $('<div>').addClass('artist').attr('id', artist['uri']).on('click', add_to_playlist_artists)
            .append(
                $('<img/>').attr('src', artist['image']).attr('alt','Artist')
            )
            .append(
                $('<span>').text(artist['name'])
            )
        );
    });
    $('#waitContainer').hide();
}

function get_artists_callback(result) {
    artists = result['artists'];
    artists.forEach( artist => {
        add_artist(artist['uri'], artist['image'], artist['name']);
    });
    $('#waitContainer').hide();
}

function get_songs_callback(result) {

    $('#waitContainer').hide();
}

$( document ).ready(function() {
    setInterval(function() {
        $.getJSON('current/', function(data, status) {
            $('#device').text(data['device']);
            $('#songname').text(data['name']);
            let artists = data['artists'];
            let artist_string = "";
            artists.forEach((element, key, arr) => {
                artist_string += element['name'];
                if (key+1 < arr.length) { artist_string += ", "};
            });
            $('#artist').text(artist_string);
            $('#current_img').attr('src', data['image']);
            $('#status').text(data['status']);
        });
    }, 15000);
    $('img#delete_playlist').on('click', function(event) {
        playlist_uri = event.currentTarget.id;
        $.getJSON('delete_playlist/'+playlist_uri, function(data, status) {
            event.currentTarget.closest('li').remove();
        });
        event.stopPropagation();
        return true;
    });
    $('ol.playlists li').on('click', function(event) {
        $('#waitContainer').show();
        playlist_uri = event.currentTarget.id;
        $.getJSON('loadplaylist/'+playlist_uri, load_playlist);
    });
    $('input#artist_lookup').keypress(function(event) {
        if (event.which == 13) {
            $('#waitContainer').show();
            $.post('artist_lookup/', { artist: $('input#artist_lookup').val(), 
                                       csrfmiddlewaretoken: csrf_token
                                     }, 
                                     lookup_artist_callback);
            return false;
        }
    });
    $('span#get_playlist_artists').on('click', function(event) {
        playlist_uri = $('input#current_playlist_uri').val();
        if (playlist_uri == '') {
            $('#messagebox_icon').attr('src', 'static/spotify/img/info.svg');
            $('#messagebox_title').text('No Playlist');
            $('#messagebox_text').text('You need to load an existing playlist from the left column.');
            $('#messagebox').show();
        } else {
            $('#waitContainer').show();
            $.getJSON('playlistartists/'+playlist_uri, get_artists_callback);
        }
    });
    $('span#clear_playlist_artists').on('click', function(event) {
        $('div#playlist_artist').empty();
    });
    $('span#clear_related_artists').on('click', function(event) {
        $('div#related_artist').empty();
    });
    $('span#get_songs_from_artists').on('click', function(event) {
        $('#waitContainer').show();
        artists = $.map($("div#playlist_artist div.artist"), function(n, i){ return n.id; });
        
        type = $('input[name="playlist_type"]:checked').val();
        if ('hipster' != type && 'popular' != type) {
            type = 'latest';
        }
        $.post('get_songs/', { artists: artists, 
                                   songs_per_artist: $('input#pl_max_tracks').val(),
                                   type: type,
                                   csrfmiddlewaretoken: csrf_token
                                 }, 
                                 get_songs_callback);
        return false;
    });
});
