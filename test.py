# import necessary modules
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, jsonify
import json

# initialize Flask app
app = Flask(__name__)

# set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# set a random secret key to sign the cookie
app.secret_key = '4653778438hfkdfd'

# set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

# route to handle logging in
@app.route('/')
def login():
    # create a SpotifyOAuth instance and get the authorization URL
    auth_url = create_spotify_oauth().get_authorize_url()
    # redirect the user to the authorization URL
    return redirect(auth_url)

# route to handle the redirect URI after authorization
@app.route('/callback')
def redirect_page():
    # clear the session
    session.clear()
    # get the authorization code from the request parameters
    code = request.args.get('code')
    # exchange the authorization code for an access token and refresh token
    token_info = create_spotify_oauth().get_access_token(code)
    # save the token info in the session
    session[TOKEN_INFO] = token_info
    # redirect the user to the save_discover_weekly route
    return redirect(url_for('save_discover_weekly',_external=True))

# route to save the Discover Weekly songs to a playlist
@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try: 
        # get the token info from the session
        token_info = get_token()
    except:
        # if the token info is not found, redirect the user to the login route
        print('User not logged in')
        return redirect("/")

    # create a Spotipy instance with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # get the user's playlists
    current_playlists =  sp.current_user_playlists()['items']
    discover_weekly_playlist_id = None
    saved_weekly_playlist_id = None

    # find the Discover Weekly and Saved Weekly playlists
    for playlist in current_playlists:
        if(playlist['name'] == 'Discover Weekly'):
            discover_weekly_playlist_id = playlist['id']
        if(playlist['name'] == 'Saved Weekly'):
            saved_weekly_playlist_id = playlist['id']
    
    # if the Discover Weekly playlist is not found, return an error message
    if not discover_weekly_playlist_id:
        return 'Discover Weekly not found.'
    
    # get the tracks from the Discover Weekly playlist
    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
    song_uris = []
    for song in discover_weekly_playlist['items']:
        song_uri= song['track']['uri']
        song_uris.append(song_uri)
    
    # add the tracks to the Saved Weekly playlist
    sp.user_playlist_add_tracks("YOUR_USER_ID", saved_weekly_playlist_id, song_uris, None)

    # return a success message
    return ('Discover Weekly songs added successfully')

# function to get the token info from the session
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        # if the token info is not found, redirect the user to the login route
        redirect(url_for('login', _external=False))
    
    # check if the token is expired and refresh it if necessary
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

@app.route('/get_username')
def get_username():
    session_data = session.get("token_info", None)
    if session_data is None:
        return redirect('/')
    
    token_info = session_data
    sp = spotipy.Spotify(auth=token_info['access_token'])

    response = sp.current_user()
    username = response["display_name"]
    return jsonify(UserName=username)


#@app.route('/topSongsPlaylist')
#def topSongsPlaylist():
    
    session_data = session.get("token_info", None)
    if session_data is None:
        return redirect('/')
    token_info = session_data
    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_songs = sp.current_user_top_tracks(limit=25, time_range="short_term")

    if 'error' in top_songs:
        print("Error from Spotify API:", top_songs['error'])

    #gets ids of top artists 
    top_song_id = [song['id'] for song in top_songs['items']]

    recommendations = []

    for i in range(0, len(top_song_id), 5):
        songs_to_recommend = top_song_id[i:i+5]
        recommended_songs = sp.recommendations(seed_tracks=songs_to_recommend, limit = 5)
        recommendations.extend(recommended_songs)

    recommended_song_id = [song['id'] for song in recommendations['tracks']]
    recommended_song_names = [song['id'] for song in recommendations['tracks']]

    song_data = {"top songs": top_songs , " recommended songs" : recommended_song_names}

    response = app.response_class(
        response=json.dumps(song_data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )

    return response

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = '5ae23f4847b44a7ebab5ff6ea0f0e5b0',
        client_secret = '3b9dfe7715104d318b6b82ff7d8ad73f',
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

app.run(debug=True)





@app.route('/topArtist')
def topArtist():
    
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('login', _external=False))  # if not logged in

    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_artists = sp.current_user_top_artists(limit=5, time_range="long_term")
    
    if 'error' in top_artists:
        print("Error from Spotify API:", top_artists['error'])

    #gets ids of top artists 
    top_artist_id = [artist['id'] for artist in top_artists['items']]

    #recommends the songs 
    recommendation_song = sp.recommendations(seed_artists=top_artist_id)
    recommended_songs = [song['name'] for song in recommendation_song['tracks']]

    # Create a new playlist
    playlist_name = "Recommended Playlist Yuval"
    playlist_description = "A playlist of recommended songs"
    sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=False, description=playlist_description)
    
    # Retrieve the ID of the newly created playlist
    playlists = sp.current_user_playlists()
    playlist_id = None
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            playlist_id = playlist['id']
            print(f"Playlist Name: {playlist['name']}")
            print(f"Playlist ID: {playlist_id}")
            break

    #gets id of recommended songs so we can add to playlist 
    recommended_song_id = [song['id'] for song in recommendation_song['tracks']]

    if playlist_id:
        # Add the recommended songs to the new playlist
        try:
            sp.user_playlist_add_tracks(user=sp.current_user()['id'], playlist_id=playlist_id, tracks=recommended_song_id)
        except Exception as e:
             print("Error adding tracks to playlist:", e)
    else:
        print("playlist is not found")


    # Return a JSON object with the recommended track names and the link to the new playlist
    recommend_playlist_data = {
        "recommended_track_names": recommended_songs,
        "playlist_link": f"https://open.spotify.com/playlist/{playlist_id}"
    }



    # Return a JSON object with the top artist names
    response_data = {"top_artists": top_artist_id , " recommended track names" : recommended_songs}

    recommend_data = {"track names" : recommended_songs}

    response = app.response_class(
        response=json.dumps(recommend_playlist_data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )

    return response