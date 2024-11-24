from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, View
from django.conf.urls.static import static
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yaml
from os import environ
import json

# Create your views here.
try:
    try:
        with open('settings/spotify.settings', 'r') as file:
            spotify_config = yaml.safe_load(file)['spotify']
    except FileNotFoundError:
        spotify_config = {}
        spotify_config['client_id'] = environ['CLIENT_ID']
        spotify_config['client_secret'] = environ['CLIENT_SECRET']
        spotify_config['redirect'] = environ['OAUTH_REDIRECT']
except KeyError:
    print('No CLIENT_ID or CLIENT_SECRET. Aborting')
    exit()

spotify_config['scope'] = "playlist-modify-public, user-read-playback-state, user-read-currently-playing, playlist-read-private, playlist-modify-private"


def getSpotify(request, code=None):
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request)
    auth_manager = SpotifyOAuth(scope=spotify_config['scope'],
                                client_id=spotify_config['client_id'],
                                client_secret=spotify_config['client_secret'],
                                redirect_uri=spotify_config['redirect'],
                                cache_handler=cache_handler,
                                show_dialog=True)
    if code is not None:
        auth_manager.get_access_token(code)
    token = cache_handler.get_cached_token()
    if token is None:
        auth_manager.get_authorize_url()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp


def get_default_context():
    context = {}
    context['app'] = 'spotify'
    context['css'] = 'spotify/css/app.css'
    return context


def get_smallest_image_url(images):
    picked_image = 'static/spotify/img/musicnote.png'
    if images is None:
        return picked_image
    height = 0
    for image in images:
        if image['height'] is None or image['height'] < height or height == 0:
            height == image['height']
            picked_image = image['url']
    return picked_image


def get_playback_info(sp):
    cp = sp.current_playback()
    playback_info = {}
    playback_info['artists'] = [{'name': ''}]
    playback_info['name'] = ''
    playback_info['uri'] = ''
    playback_info['device'] = ''
    playback_info['image'] = 'static/spotify/img/musicnote.png'
    playback_info['left'] = ''
    playback_info['status'] = ''
    if cp is not None and cp['is_playing']:
        playback_info['device'] = cp['device']['name']
        playback_info['artists'] = cp['item']['artists']
        playback_info['name'] = cp['item']['name']
        playback_info['uri'] = cp['item']['uri']
        playback_info['left'] = cp['item']['duration_ms'] - cp['progress_ms']
        playback_info['image'] = get_smallest_image_url(cp['item']['album']['images'])
        playback_info['status'] = 'Playing on '
    return playback_info


class SpotifyIndex(TemplateView):
    template_name = "spotify/index.html"

    def get_context_data(self, **kwargs):
        return get_default_context()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        print('index')
        sp = getSpotify(request)
        if sp.auth_manager.cache_handler.get_cached_token() is None:
            return redirect(sp.auth_manager.get_authorize_url())
        user = sp.me()
        context['username'] = user['display_name']
        context['userlink'] = user['external_urls']

        context['pi'] = get_playback_info(sp)
        pl = sp.current_user_playlists()
        playlists = []
        for item in pl['items']:
            plist = {}
            plist['image'] = get_smallest_image_url(item['images'])
            plist['id'] = item['id']
            plist['uri'] = item['uri']
            plist['name'] = item['name'][:32]
            playlists.append(plist)
        context['playlists'] = playlists
        return self.render_to_response(context)


class SpotifyCallback(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        print(code)
        sp = getSpotify(request, code)
        user = sp.me()
        print(user)
        return redirect(reverse('spotify:index'))


def current(request):
    print('current')
    sp = getSpotify(request)
    if sp.auth_manager.cache_handler.get_cached_token() is None:
        return redirect(sp.auth_manager.get_authorize_url())
    playback_info = get_playback_info(sp)
    return HttpResponse(json.dumps(playback_info), content_type='application/json')


def get_playlist_tacks(sp, playlist, fields):
    limit = 100
    offset = 0
    total = 500
    tracks = []
    while offset < total:
        tracklist = sp.playlist_tracks(playlist, 'total,' + fields, limit=limit, offset=offset)
        total = tracklist['total']
        for t in tracklist['items']:
            track = {}
            if 'track' in t:
                t = t['track']
            if 'album' in t:
                if 'name' in t['album']:
                    track['album'] = t['album']['name']
                if 'images' in t['album']:
                    track['image'] = get_smallest_image_url(t['album']['images'])
            if 'name' in t:
                track['name'] = t['name']
            if 'artists' in t:
                track['artists'] = t['artists']
            if 'uri' in t:
                track['uri'] = t['uri']
            tracks.append(track)
        offset += limit
    return tracks


def load_playlist(request, uri):
    print('load_playlist')
    sp = getSpotify(request)
    if sp.auth_manager.cache_handler.get_cached_token() is None:
        return redirect(sp.auth_manager.get_authorize_url())
    print(uri)
    data = {'playlist': {}, 'tracks': []}
    playlist = sp.playlist(uri, 'id, images, name, owner, uri, description, tracks(total)')
    data['playlist']['name'] = playlist['name']
    data['playlist']['description'] = playlist['description']
    data['playlist']['image'] = get_smallest_image_url(playlist['images'])
    data['playlist']['trackcount'] = playlist['tracks']['total']
    data['playlist']['uri'] = playlist['uri']
    data['tracks'] = get_playlist_tacks(sp, uri, 'items(track(name,artists(name),uri,album(name,images)')
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_playlist(request, uri):
    data = {'status': 'OK'}
    print(uri)
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_track_from_playlist(request, playlist, track):
    data = {'status': 'OK'}
    print(playlist)
    print(track)
    return HttpResponse(json.dumps(data), content_type='application/json')


def artist_lookup(request):
    data = {'status': 'OK'}
    q = 'artist:' + request.POST.get('artist', '')
    sp = getSpotify(request)
    if sp.auth_manager.cache_handler.get_cached_token() is None:
        return redirect(sp.auth_manager.get_authorize_url())
    result = sp.search(q, limit=10, offset=0, type="artist")
    artists = []
    for artist in result['artists']['items']:
        a = {
            'name': artist['name'],
            'image': get_smallest_image_url(artist['images']),
            'uri': artist['uri'],
            'genres': ','.join([x for x in artist['genres']])
        }
        artists.append(a)
    data['artists'] = artists
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_artists_from_playlist(request, uri):
    data = {'status': 'OK'}
    sp = getSpotify(request)
    if sp.auth_manager.cache_handler.get_cached_token() is None:
        return redirect(sp.auth_manager.get_authorize_url())
    tracks = get_playlist_tacks(sp, uri, 'items(track(artists(uri)')
    # uris = set([y['uri'] for x in tracks for y in x['artists']])
    uris = set([y[0]['uri'] for y in [x['artists'] for x in tracks]])
    sp_artists = sp.artists(uris)
    artists = []
    for sp_artist in sp_artists['artists']:
        artist = {}
        artist['name'] = sp_artist['name']
        artist['image'] = get_smallest_image_url(sp_artist['images'])
        artist['uri'] = sp_artist['uri']
        artist['genres'] = ', '.join(sp_artist['genres'])
        artists.append(artist)
    data['artists'] = artists
    return HttpResponse(json.dumps(data), content_type='application/json')
