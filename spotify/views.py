from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import yaml

# Create your views here.
with open('settings/spotify.settings', 'r') as file:
    spotify_config = yaml.safe_load(file)['spotify']

def getSpotifyAuth(request):
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request)
    return SpotifyPKCE(scope=spotify_config['scope'], 
                        client_id=spotify_config['client_id'],
                        #client_secret=spotify_config['client_secret'],
                        redirect_uri=spotify_config['redirect'],
                        cache_handler=cache_handler,
                        open_browser=True)

class SpotifyIndex(TemplateView):
    template_name = "index.html"
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        print('index')
        auth_manager=getSpotifyAuth(request)
        #cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request)
        #auth_manager = SpotifyClientCredentials(client_id=spotify_config['client_id'], client_secret=spotify_config['client_secret'], cache_handler=cache_handler)
        sp = spotipy.Spotify(client_credentials_manager=auth_manager)
        user = sp.me()
        print(user)
        return self.render_to_response(context)

class SpotifyCallback(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        auth_manager=getSpotifyAuth(request)
        auth_manager.get_access_token(code)
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        user = sp.me()
        print(user)
        return HttpResponse("OK")