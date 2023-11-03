from flask import Flask, redirect, request, session, url_for, render_template_string
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # This should be a secure and secret key in a real application

SPOTIPY_CLIENT_ID = '8b012495786d401d930e6b983d3490c9'
SPOTIPY_CLIENT_SECRET = 'b254500e47c649fc9dbcb9495ed6b7ec'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=url_for('redirectPage', _external=True),  # Dynamic generation of redirect_uri
        scope="user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-private"
    )

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('getTracks'))

@app.route('/getTracks')
def getTracks():
    
    token_info = session.get("token_info")
    if not token_info:
        return redirect(url_for('login'))

    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))
    sp = Spotify(auth=token_info['access_token'])
    tracks = sp.current_user_top_tracks(limit=10)
    # Render tracks or return them as you wish
    return render_template_string("<ul>{% for track in tracks['items'] %}<li>{{ track['name'] }}</li>{% endfor %}</ul>", tracks=tracks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
