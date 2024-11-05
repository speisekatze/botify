from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, View
from django.conf.urls.static import static
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yaml
import json

# Create your views here.
with open('settings/spotify.settings', 'r') as file:
    spotify_config = yaml.safe_load(file)['spotify']

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
        t = auth_manager.get_authorize_url()
        #return t
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
        sp=getSpotify(request)
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
        sp=getSpotify(request, code)
        user = sp.me()
        print(user)
        return redirect(reverse('spotify:index'))
    


def current(request):
    print('current')
    sp=getSpotify(request)
    if sp.auth_manager.cache_handler.get_cached_token() is None:
        return redirect(sp.auth_manager.get_authorize_url())
    playback_info = get_playback_info(sp)
    return HttpResponse(json.dumps(playback_info),content_type='application/json')

def load_playlist(request, uri):
    print('load_playlist')
    sp=getSpotify(request)
    if sp.auth_manager.cache_handler.get_cached_token() is None:
        return redirect(sp.auth_manager.get_authorize_url())
    print(uri)
    data = { 'playlist': {}, 'tracks': []}
    playlist = sp.playlist(uri, 'id, images, name, owner, uri, description, tracks(total)')
    data['playlist']['name'] = playlist['name']
    data['playlist']['description'] = playlist['description']
    data['playlist']['image'] = get_smallest_image_url(playlist['images'])
    data['playlist']['trackcount'] = playlist['tracks']['total']
    data['playlist']['uri'] = playlist['uri']
    limit = 100
    offset = 0
    tracks = []
    while offset < data['playlist']['trackcount']:
        tracklist = sp.playlist_tracks(uri,'items(track(name,artists(name),uri,album(name,images)', limit=limit, offset=offset)
        for t in tracklist['items']:
            track = {}
            t = t['track']
            track['image'] = get_smallest_image_url(t['album']['images'])
            track['album'] = t['album']['name']
            track['name'] = t['name']
            track['artists'] = t['artists']
            track['uri'] = t['uri']
            tracks.append(track)
        offset += limit
    data['tracks'] = tracks
    return HttpResponse(json.dumps(data),content_type='application/json')

def delete_playlist(request, uri):
    data = { 'status': 'OK' }
    print(uri)
    return HttpResponse(json.dumps(data),content_type='application/json')

def delete_track_from_playlist(request, playlist, track):
    data = { 'status': 'OK' }
    print(playlist)
    print(track)
    return HttpResponse(json.dumps(data),content_type='application/json')