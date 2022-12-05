import json
import requests
import torch
from flask import render_template, Blueprint, request, redirect, url_for, session
from transformers import pipeline
classifier = pipeline("text-classification", model="dinolii/ece1786", tokenizer="dinolii/ece1786", return_all_scores=True)
result_blueprint = Blueprint('result_bp', __name__, template_folder='templates')


@result_blueprint.route("/recommend", methods=['GET', 'POST'])
def recommend():
    user_input = request.form.get('user_input')
    if not user_input:
        return redirect(url_for('input_bp.input'))
    classification_result = classifier(user_input)[0]
    classification_result = [classification_result[0]['score'], classification_result[1]['score'], classification_result[2]['score'], classification_result[3]['score'], classification_result[4]['score']]

    params = {'seed_genres': "pop", 'seed_artists': "", 'seed_tracks': ""}
    # neutral
    if classification_result[4] > 0.5:
        params['popularity'] = 1.0
        params['valence'] = 0.5
    # happy
    if classification_result[0] > 0.5:
        params['seed_genres'] += ',happy'
        params['danceability'] = max(0.6, classification_result[0])
    # surprise
    if classification_result[1] > 0.5:
        params['popularity'] = 0.1
    # disgust
    if classification_result[2] > 0.5:
        params['seed_genres'] += ',sad'
    # anger
    if classification_result[3] > 0.5:
        if params.get("valence"):
            params.pop("valence")
        params['valence'] = min(0.35, 1 - classification_result[3])
        params['energy'] = max(0.6, classification_result[3])

    if request.method == 'POST':
        print(params)
        get_reccomended_url = f"https://api.spotify.com/v1/recommendations?limit=25"
        response = requests.get(get_reccomended_url,
                                headers=session['authorization_header'],
                                params=params).text
        tracks = list(json.loads(response)['tracks'])
        tracks_uri = [track['uri'] for track in tracks]
        session['tracks_uri'] = tracks_uri
        data = {}
        data["tracks"] = tracks
        data["classification_result"] = classification_result
        return render_template('result.html', data=data)

    return redirect(url_for('input_bp.input'))


@result_blueprint.route("/result", methods=['GET', 'POST'])
def result():

    authorization_header = session['authorization_header']
    user_profile_api_endpoint = f"https://api.spotify.com/v1/me"
    profile_data = requests.get(user_profile_api_endpoint, headers=authorization_header).text
    profile_data = json.loads(profile_data)
    user_id = profile_data['id']

    playlist_name = request.form.get('playlist_name')
    playlist_data = json.dumps({
        "name": playlist_name,
        "description": "Recommended songs",
        "public": True
    })

    create_playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    response = requests.post(create_playlist_url,
                             headers=authorization_header,
                             data=playlist_data).text

    playlist_id = json.loads(response)['id']

    tracks_uri = session['tracks_uri']
    tracks_data = json.dumps({
        "uris": tracks_uri,
    })

    add_items_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.post(add_items_url, headers=authorization_header, data=tracks_data).text

    return render_template('listen.html', playlist_id=playlist_id)
