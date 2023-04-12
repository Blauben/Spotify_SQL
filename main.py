import secrets
import hashlib
import base64
import requests
import urllib.parse
import webbrowser

client_id = "2a82f25dce394acf95ba010d27fd6225"
auth_url = "https://accounts.spotify.com/authorize/"
redirect_uri = "http://localhost:8080"


def code_challenge():
    secret = secrets.token_hex(128).encode()
    secret = hashlib.sha256(secret)
    return base64.b64encode(secret.digest())


def listen_for_http_response_code():
    return input("Code eingeben:\n")


def fetch_Token():
    state = secrets.token_hex(16)
    param = {"response_type": "code", "client_id": client_id, "scope": "user-read-private user-read-email",
             "redirect_uri": redirect_uri, "state": state, "code_challenge_method": "S256",
             "code_challenge": code_challenge()}
    with requests.Session() as session:
        rep = session.get(auth_url, params=param)
    webbrowser.open(rep.url)
    code = listen_for_http_response_code()


def main():
    fetch_Token()


if __name__ == "__main__":
    main()
