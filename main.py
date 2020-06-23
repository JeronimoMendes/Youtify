from flask import Flask, render_template, request, redirect, sessions, session
from script import converter, get_id, get_name
from urllib.parse import urlencode
import requests
import json
from credentials import ID, SECRET, FLASK_KEY
  
# mudar no host: "http://jeronimomendes.pythonanywhere.com/spotify/callback"

###### Credenciais necessarias para utilizar a API do Spotify ######
auth_header = None
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

CLIENT_ID = ID
CLIENT_SECRET = SECRET

REDIRECT_URI = 'http://127.0.0.1:5000/spotify/callback'
SCOPES = 'playlist-modify-public'
provider_url = "https://accounts.spotify.com/authorize"

params = urlencode({
    'client_id': CLIENT_ID,
    'scope': SCOPES,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code'
})

spotify_auth_url = provider_url + '?' + params

app = Flask(__name__)

# Allows the use of cookie 
app.secret_key = FLASK_KEY

@app.route('/')
def home():
  return render_template("index.html")

@app.route('/about')
def about():
  return render_template("about.html")


@app.route('/yt', methods=["POST","GET"])
def yt():
  if request.method == "POST":
    req = request.form

    session['yt_url'] = req["yt_url"]

    return redirect("spotify")

  return render_template("youtube.html")


@app.route('/spotify')
def spotify(): 
  
  return render_template("spotify.html", link=spotify_auth_url)

@app.route('/spotify/callback')
def spotify_callback():

  auth_token = request.args['code']
  code_payload = {
      "grant_type": "authorization_code",
      "code": str(auth_token),
      "redirect_uri": REDIRECT_URI,
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET,
  }
  post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

  response_data = json.loads(post_request.text)

  access_token = response_data["access_token"]

  session['access_token'] = access_token

  spot_id = get_id(access_token)
  session['id'] = spot_id
  
  return redirect("/playlistInfo")

@app.route("/playlistInfo", methods=["POST","GET"])
def playlistInfo():
  nome = get_name(session['access_token'])

  if request.method == "POST":
    req = request.form

    session['name_playlist'] = req["nome_playlist"]
    session['descr_playlist'] = req["descr_playlist"]

    return redirect("/loading")

  return render_template("playlistInfo.html", username = nome)

@app.route('/loading')
def loading():
  return render_template('loading.html')

@app.route("/done")
def conversao():
  converter(session['access_token'], session['id'], session['yt_url'], session['name_playlist'], session['descr_playlist'])

  session.clear()
  return render_template("done.html")

@app.errorhandler(404)
def not_found_404(e):
  return render_template("error.html"), 404

@app.errorhandler(500)
def not_found_500(e):
  return render_template("error.html"), 500

if __name__ == "__main__":
  app.run()
