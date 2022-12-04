import os
from flask import Blueprint, request, redirect, url_for, session, render_template

from app.spotify_api.spotify_client import SpotifyClient

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

spotify_client = SpotifyClient(client_id, client_secret, port=8002)
login_blueprint = Blueprint('login_bp', __name__, template_folder='templates')


@login_blueprint.route("/")
def loginPage():
    return render_template('login.html')


@login_blueprint.route("/login", methods=['POST', 'GET'])
def login():
    """
    redirect to Spotify's log in page
    """
    auth_url = spotify_client.get_auth_url()
    return redirect(auth_url)


@login_blueprint.route("/callback")
def callback():
    """
    set the session's authorization header
    """
    auth_token = request.args['code']
    spotify_client.get_authorization(auth_token)
    authorization_header = spotify_client.authorization_header
    session['authorization_header'] = authorization_header
    print(authorization_header)
    return redirect(url_for("input_bp.input"))
