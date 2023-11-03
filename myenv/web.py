import os
from flask import Flask, redirect, request, session, jsonify
from spotipy import Spotify, oauth2

# Replace these with your actual Spotify Developer credentials
CLIENT_ID = "5ae23f4847b44a7ebab5ff6ea0f0e5b0"
CLIENT_SECRET = "3b9dfe7715104d318b6b82ff7d8ad73f"
REDIRECT_URI = "http://localhost:8080/callback"  # This should match the Redirect URI in your Spotify Developer Dashboard
SCOPE = "user-read-private"

# Flask app
app = Flask(__name__)
app.secret_key = os.urandom(64)  # A random secret key for session management

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect('/get_username')

@app.route('/get_username')
def get_username():
    session_data = session.get("token_info", None)
    if session_data is None:
        return redirect('/')
    
    token_info = session_data
    sp = Spotify(auth=token_info["access_token"])
    response = sp.current_user()
    username = response["display_name"]
    return jsonify(UserName=username)

def create_spotify_oauth():
    return oauth2.SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = REDIRECT_URI,
        scope = SCOPE
    )

if __name__ == "__main__":
    app.run(debug=True, port=8080)
