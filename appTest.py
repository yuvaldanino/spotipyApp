from flask import Flask, request, url_for, session, redirect, jsonify
import spotipy 
from spotipy.oauth2 import SpotifyOAuth
import time 
import json


app = Flask(__name__)

app.debug = False

app.secret_key = 'ONDdff234fdfasssf32HGHJ'
app.config['SESSION_COOKIE_NAME'] = 'Yuvals Cookies'
TOKEN_INFO = "token_info"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


@app.route('/')
def login():
    if 'user_data' in session:
        session[TOKEN_INFO] = "token_info_{}".format(session['user_data']['id'])
        return redirect(url_for('getTracks', _external=True))
    else:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)



@app.route('/redirect')
def redirectPage():

    sp_oauth = create_spotify_oauth()
    #session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    #session[TOKEN_INFO] = token_info
    session['access_token'] = token_info['access_token']

    return redirect(url_for('getTracks', _external = True))



@app.route('/getTracks')
def getTracks():
    
    if 'access_token' in session:
        user_access_token = session['access_token']
        sp = spotipy.Spotify(auth=user_access_token)
    else:
        print("User not logged in")
        return redirect(url_for('login', _external=False))

    saved_tracks = []
    top_tracks = []
    offset = 0
    limit = 50  # Set the number of items to retrieve per request

    while True:
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)

        items = response['items']
        saved_tracks.extend(items)
        offset += limit
        if len(items) < limit:
            break

    song_names = [item['track']['name'] for item in saved_tracks]
    id_names = [item['track']['id'] for item in saved_tracks]

    size = len(song_names)

    userInfo = sp.current_user()
    userName = userInfo['display_name']

    user_link = userInfo['href']

    # Return a JSON object with song names and the number of saved tracks
    response_data = {"userName": userName,"User Link":user_link, "songs": song_names,"id's": id_names, "size": size}

    connection_data = {"userName": userName}

    response = app.response_class(
        response=json.dumps(response_data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )

    return response

@app.route('/getTopTracksFeatures')
def get_top_tracks_features():
    if 'access_token' not in session:
        print("User not logged in")
        return redirect(url_for('login', _external=False))

    user_access_token = session['access_token']
    sp = spotipy.Spotify(auth=user_access_token)

    # Fetch the user's top tracks; limit is set to 10 for the top tracks
    top_tracks_response = sp.current_user_top_tracks(limit=10, time_range='medium_term')
    top_tracks = top_tracks_response['items']

    # Extract track IDs and names
    track_ids = [track['id'] for track in top_tracks]
    track_names = [track['name'] for track in top_tracks]

    # Get the audio features for the top 10 track IDs
    audio_features = sp.audio_features(track_ids)

    # Create a list of dictionaries with the track name and its features
    tracks_with_features = []
    for i, features in enumerate(audio_features):
        if features:  # Only proceed if features are found
            track_info = {
                'name': track_names[i],
                'features': {
                    'acousticness': features['acousticness'],
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'instrumentalness': features['instrumentalness'],
                    'liveness': features['liveness'],
                    'loudness': features['loudness'],
                    'speechiness': features['speechiness'],
                    'tempo': features['tempo'],
                    'valence': features['valence']
                }
            }
            tracks_with_features.append(track_info)

    # Prepare the JSON response
    response_data = json.dumps(tracks_with_features, ensure_ascii=False)

    # Create and send a response object
    response = app.response_class(
        response=response_data,
        status=200,
        content_type="application/json; charset=utf-8"
    )

    return response



def get_token():
    token_info = session.get(TOKEN_INFO, None)
    
    if token_info:
        # Access token is cached, you can log it or perform further actions
        print("Cached Access Token:", token_info['access_token'])
    else:
        # Access token is not cached, handle this case as needed
        print("Access Token not found in session")
    
    if not token_info:
        raise Exception("Access token not found")
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info
        


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "8b012495786d401d930e6b983d3490c9" ,
        client_secret = "8aa308a3d32942c495c0468b014871b5",
        redirect_uri = url_for( 'redirectPage', _external= True), # so i dont need to hard code local host 
        scope = "user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-private"
        ) 
    
if __name__ == '__main__':
    app.run()

@app.route('/relogin')
def relogin():
    # Clear the existing session to log out the user
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login', _external=True))
