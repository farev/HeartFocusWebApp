import os

from flask import Flask, request, redirect, session, url_for

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = 'd196ffdec4734d30a407cc6946381981'
client_secret = '6cc086bb56db461dba5829eb20fe83b7'
redirect_uri = 'http://localhost:8000/callback'
scope = 'user-top-read'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id = client_id,
    client_secret = client_secret,
    redirect_uri = redirect_uri,
    scope = scope,
    cache_handler = cache_handler,
    show_dialog = True
)
sp = Spotify(auth_manager=sp_oauth)
info_list = []
#artist_list = []
track_list = []

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    for i in info_list:
        print(i)
    return redirect(url_for('get_top_artists'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    for i in info_list:
        print(i)
    return redirect(url_for('get_top_tracks'))

#@app.route('/get_top_artists')
#def get_top_artists():
    #if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        #auth_url = sp_oauth.get_authorize_url()
        #return redirect(auth_url)
    
    #top_artists = sp.current_user_top_artists(limit=5)
    #top_artists_info = [(ta['name'], ta['external_urls']['spotify']) for ta in top_artists['items']]
    #top_artists_html = '<br>'.join([f'{name}: {url}' for name, url in top_artists_info])
    #print(top_artists_info)
    #info_list.append(top_artists_info)
    #for artist in top_artists_info:
        #print((artist[1].split('artist/', 1))[1])
        #artist_list.append(artist[1])
    #print(artist_list)
    ##return redirect(url_for('get_top_tracks'))

@app.route('/get_top_tracks')
def get_top_tracks():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    top_tracks = sp.current_user_top_tracks(limit=5)
    top_tracks_info = [(ta['name'], ta['external_urls']['spotify']) for ta in top_tracks['items']]
    top_tracks_html = '<br>'.join([f'{name}: {url}' for name, url in top_tracks_info])
    #print(top_tracks_info)
    info_list.append(top_tracks_info)
    for track in top_tracks_info:
        #print((track[1].split('track/', 1))[1])
        track_list.append(track[1])
    return redirect(url_for('recommendations'))

@app.route('/recommendations')
def recommendations():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    recommended = sp.recommendations(seed_tracks=track_list, country='US', limit=1, target_tempo=100)
    print(recommended["tracks"][0]["external_urls"]["spotify"])
    return "Everything is fine"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

    