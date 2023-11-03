from flask import Flask, request, url_for, session, redirect, jsonify
import spotipy 
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import time 
import json


app = Flask(__name__)

app.debug = False

app.secret_key = 'ONDdff234fdfasf32HGHJ'
app.config['SESSION_COOKIE_NAME'] = 'Yuvals Cookies'
TOKEN_INFO = "token_info"

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


#@app.route('/')
#def login():
    #token_info = session.get(TOKEN_INFO)

    #if token_info:
        #return redirect(url_for('getTracks'))
    #else:
       # sp_oauth = create_spotify_oauth()
       # auth_url = sp_oauth.get_authorize_url()
       # return redirect(auth_url)
    
    
@app.route('/')
def login():
    print(f"Session in login route: {session}")
    if 'user_data' in session:
        session[TOKEN_INFO] = "token_info_{}".format(session['user_data']['id'])
        return redirect(url_for('getTracks', _external=True))
    elif TOKEN_INFO in session:  # token_info is present but user_data isn't
        session.pop(TOKEN_INFO, None)  # remove the stale token_info
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)



@app.route('/redirect')
def redirectPage():
    print(f"Session after getting token: {session}")

    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['access_token'] = token_info['access_token']

    # Get user profile data
    sp = spotipy.Spotify(auth=session['access_token'])
    user_data = sp.current_user()
    session['user_data'] = user_data

    return redirect(url_for('getTracks', _external=True))



#@app.route('/getTracks')
#def getTracks():
    
    if 'access_token' in session:
        user_access_token = session['access_token']
        sp = spotipy.Spotify(auth=user_access_token)
    else:
        print("User not logged in")
        return redirect(url_for('login', _external=False))
    
    '''
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('login', _external = False)) # if not logged in 
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    '''

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

@app.route('/getTracks')
def getTracks():
    print(f"Session in getTracks: {session}")


    # Check if user_data exists in the session
    if 'user_data' not in session:
        print("User not logged in")
        return redirect(url_for('login'))

    # Fetch user's name from session
    user_name = session['user_data']['display_name']
    return f"Hello, {user_name}! Show user's tracks here."



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

#top 25 songs playlist 
@app.route('/topSongsPlaylist')
def topSongsPlaylist():
    
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('login', _external=False))  # if not logged in

    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_songs = sp.current_user_top_tracks(limit=25, time_range="short_term")

    if 'error' in top_songs:
        print("Error from Spotify API:", top_songs['error'])

    #gets ids of top artists 
    top_song_id = [song['id'] for song in top_songs['items']]
    top_song_names = [song['name'] for song in top_songs['items']]


    recommendations = []

    for i in range(0, len(top_song_id), 5):
        songs_to_recommend = top_song_id[i:i+5]
        recommended_songs = sp.recommendations(seed_tracks=songs_to_recommend, limit = 5)
        recommendations.extend(recommended_songs['tracks'])

    recommended_song_id = [song['id'] for song in recommendations]
    recommended_song_names = [song['name'] for song in recommendations]

    #JSON object
    song_data = {"top songs": top_song_names , " recommended songs" : recommended_song_names}
    response = app.response_class(
        response=json.dumps(song_data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )

    # Create a new playlist
    playlist_name = "top 25 Recommended Playlist "
    playlist_description = "A playlist of recommended songs based on top 25"
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
    
    if playlist_id:
        # Add the recommended songs to the new playlist
        try:
            sp.user_playlist_add_tracks(user=sp.current_user()['id'], playlist_id=playlist_id, tracks=recommended_song_id)
        except Exception as e:
             print("Error adding tracks to playlist:", e)
    else:
        print("playlist is not found")

    

    return response

@app.route('/topTrackFeatures')
def topTrackFeatures():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('login', _external=False))  # if not logged in

    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_tracks = sp.current_user_top_tracks(limit=10, time_range="long_term")
    
    # Get IDs of top songs 
    top_track_ids = [track['id'] for track in top_tracks['items']]
    
    # Get names of top songs 
    top_track_names = [track['name'] for track in top_tracks['items']]

    # Get audio features for each top song
    features = sp.audio_features(tracks=top_track_ids)

    # Now extract the features for each song
    features_list = [{ 
        'danceability': track['danceability'],
        'energy': track['energy'],
        'key': track['key'],
        'loudness': track['loudness'],
        'mode': track['mode'],
        'speechiness': track['speechiness'],
        'acousticness': track['acousticness'],
        'instrumentalness': track['instrumentalness'],
        'liveness': track['liveness'],
        'valence': track['valence'],
        'tempo': track['tempo']
    } for track in features]

    response_data = {
        "top_tracks": top_track_names,
        "audio_features": features_list
    }

    response = app.response_class(
        response=json.dumps(response_data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )

    return response


    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('login', _external=False))  # if not logged in

    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_tracks = sp.current_user_top_tracks(limit=10, time_range="long_term")

    #gets ids of top songs 
    top_song_id = [artist['id'] for artist in top_tracks['items']]
    
    #gets name of top songs 
    top_song_name = [artist['name'] for artist in top_tracks['items']]

    features = sp.audio_features(tracks = top_song_id)

    features_danceability = [song['danceability'] for song in features]

    response_data = {"top_tracks": top_song_name , "features dancibility" : features_danceability}

    response = app.response_class(
        response=json.dumps(response_data, ensure_ascii=False),
        status=200,
        content_type="application/json; charset=utf-8"
    )

    return response

    #return jsonify(response_data)



#need to do this run loop where it finds most recent 5 songs recommends and does it a coule times to recommend hella songs. maybe do for each 5 songs recommend 5 a couple times. 
@app.route('/recentSongsNewPlaylist')
def recentSongsNewPlaylist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('login', _external=False))  # if not logged in

    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_tracks = sp.current_user_top_tracks(limit=10, time_range="long_term")



    return "yeet"


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
        scope = "user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-private user-read-private"
        )   
    
if __name__ == '__main__':
    app.run()

@app.route('/relogin')
def relogin():
    session.clear()
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_data', None)
    session.pop(TOKEN_INFO, None)
    return redirect(url_for('login', _external=True))


