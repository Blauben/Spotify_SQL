import json
import random
import secrets
import hashlib
import base64
import string

from queue import Queue
import threading
import requests
import webbrowser
import http.server
import socketserver
import re

clientId = "2a82f25dce394acf95ba010d27fd6225"
authUrl = "https://accounts.spotify.com/authorize/"
tokenUrl = "https://accounts.spotify.com/api/token/"
redirectUri = "http://localhost:8080"

codeQueue = Queue()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(
            "<html><head><h1>Code erfolgreich empfangen!</h1></head><body>Dieser Tab kann nun geschlossen werden.</body></html>",
            "utf-8"))
        code = re.search(".*?code=(.*)&", self.path).group(1)
        codeQueue.put(code)


def generateCodeVerifier():
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(127))


def generateCodeChallenge(verifier):
    challenge = hashlib.sha256(verifier.encode())
    challenge = base64.b64encode(challenge.digest())
    challenge = challenge.replace(b"+", b"-")
    challenge = challenge.replace(b"/", b"_")
    return challenge.replace(b"=", b"")


codeVerifier = generateCodeVerifier()


def fetch_Code():
    state = secrets.token_hex(16)
    codeChallenge = generateCodeChallenge(codeVerifier)
    param = {"response_type": "code", "client_id": clientId, "scope": "user-read-private user-read-email",
             "redirect_uri": redirectUri, "state": state, "code_challenge_method": "S256",
             "code_challenge": codeChallenge}
    with requests.Session() as session:
        rep = session.get(authUrl, params=param)
    webbrowser.open(rep.url)


def fetch_Token(code):
    param = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirectUri, "client_id": clientId,
             "code_verifier": codeVerifier}
    with requests.Session() as session:
        rep = session.post(tokenUrl, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=param)
        rep = json.loads(rep.text)
        return rep["access_token"]


def accessToken():
    server = socketserver.TCPServer(("localhost", 8080), Handler)
    serverThread = threading.Thread(target=server.serve_forever)
    serverThread.daemon = True
    serverThread.start()

    fetch_Code()
    while codeQueue.qsize() == 0:
        continue
    server.shutdown()
    serverThread.join()

    return fetch_Token(codeQueue.get())


def main():
    print(f"Access Token: {accessToken()}")


if __name__ == "__main__":
    main()
