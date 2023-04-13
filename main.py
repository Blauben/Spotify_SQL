import json
import os

from spotify_auth import spotifyTokens
import requests
from os.path import exists

spotifyApiBaseUrl = "https://api.spotify.com/v1"
tokens = spotifyTokens()

with requests.Session() as session:
    rep = session.get(f"{spotifyApiBaseUrl}/me/playlists", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    print(json.loads(rep.text))
