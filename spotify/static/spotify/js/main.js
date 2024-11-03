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
    $('ol.playlists li').on('click', function(event) {
        $('#waitContainer').show();
        $.getJSON('loadplaylist/'+event.target.id, function(data, status) {
            console.info(data);
            pl_info = data['playlist'];
            $('#playlist_name').text(pl_info['name']);
            /*$('#playlist_desc').text(pl_info['description']);*/
            $('#playlist_count').text(pl_info['trackcount']);
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
            $('#waitContainer').hide()
        });
    });
});