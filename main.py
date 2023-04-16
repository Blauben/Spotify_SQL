import json
from dataclasses import dataclass

from spotify_auth import spotifyTokens
from spotify_auth import checkTokenValidity
import requests

spotifyApiBaseUrl = "https://api.spotify.com/v1"
tokens = spotifyTokens()


class TokenExpired(Exception):
    def __init__(self):
        message = "Spotify Authentication has expired. Please rerun the application!"
        super().__init__(message)


class BadRequest(Exception):
    def __init__(self, url, header="None"):
        message = f"Request to Spotify URI Endpoint {url} failed with header={header}"
        super().__init__(message)

@dataclass
class Track:
    trackID: str
    name: str
@dataclass
class Playlist:
    playlistID: str
    name: str


def handleRequestError(url):
    global tokens
    if not checkTokenValidity(tokens["access_token"]):
        tokens = spotifyTokens()


def fetchPlaylists(url=None):
    with requests.Session() as session:
        url = f"{spotifyApiBaseUrl}/me/playlists" if url is None else url
        rep = session.get(url,
                          headers={"Authorization": f"Bearer {tokens['access_token']}"})
        handlePossibleRequestCodeError(rep.status_code, url=rep.url, header=rep.headers)
    rawJSON = json.loads(rep.text)
    playlists = list(map(lambda item: Playlist(item["id"], item["name"]), rawJSON["items"]))
    if rawJSON["next"] is not None:
        playlists.append(fetchPlaylists(url=rawJSON["next"]))
    return playlists


def fetchTracks(playlist_id):
    with requests.Session() as session:
        url = f"{spotifyApiBaseUrl}/playlists/{playlist_id}/tracks"
        rep = session.get(url,
                          headers={"Authorization": f"Bearer {tokens['access_token']}"})
        handlePossibleRequestCodeError(rep.status_code, url=rep.url, header=rep.headers)
        rawJSON = json.loads(rep.text)
        tracks = list(map(lambda item: Track(item["track"]["id"], item["track"]["name"]), rawJSON["items"]))
        print(tracks)
        #TODO load next pages and look for genre attribute



def handlePossibleRequestCodeError(status_code, url="URL_MISSING", header="None"):
    if status_code == 401:
        raise TokenExpired
    elif status_code != 200:
        raise BadRequest(url, header=header)


def main():
    playlists = fetchPlaylists()
    fetchTracks(playlists[0].playlistID)


if __name__ == "__main__":
    main()
