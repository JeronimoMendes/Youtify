import json
import webbrowser
import requests
from pyyoutube import Api
import re
from credentials import YOUTUBE_KEY
    

# ----------------------------------------------Spotify------------------------------------------------------

def get_id(token):
  #Returns the user's ID

  query = "https://api.spotify.com/v1/me"
  profile_response = requests.get(query, headers={
          "Authorization": "Bearer {}".format(token)
      })

  profile_data = json.loads(profile_response.text)

  return profile_data["id"]


def get_name(token):
  #Returns the user's spotify name

  query = "https://api.spotify.com/v1/me"
  profile_response = requests.get(query, headers={
          "Authorization": "Bearer {}".format(token)
      })

  profile_data = json.loads(profile_response.text)

  return profile_data["display_name"]



def create_playlist(spotify_token,nome_playlist, descr_playlist, user_id):
    #Creates a new spotify playlist and return it's ID
    request_body = json.dumps({
        "name": "{}".format(nome_playlist),
        "description": "{}".format(descr_playlist),
        "public": True
    })

    query = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = json.loads(response.text)

    return response_json["id"]

def search_music(m, token):
    #Returns ID of searched music
    query = "https://api.spotify.com/v1/search?q={}&type=track&limit=3".format(m)

    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
        }
    )
    response_json = response.json()

    try:
        musica_spotify = response_json["tracks"]["items"][0]["uri"]
        print("This music was found: {}".format(musica_spotify))
        return musica_spotify
    except:
        print("This music wasn't found: {}".format(m))


def add_music(id_playlist, musicas_playlist, token):
    #Adds musics to Spotify playlist
    request_data = json.dumps(musicas_playlist)

    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(id_playlist)
    
    print(request_data)
    response = requests.post(
        query,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
        }
    )
    response_json = response.json()
    print("Musicas adicionadas!")
    return response_json

def filter_music(item):
    #Filters unwanted words in music titles

    item1 = [] 
    words= ["OFFICIAL", "VIDEO", "ALBUM", "VERSION", "AUDIO", "(", ")",
                    "MUSIC VIDEO", "LYRICS", "[", "]", "MUSIC", "HD",
                     "CLIPE", "OFICIAL","VIDEO", "LYRIC", "PROD.", "LETRA"] 
    for line in item:
        for w in words:
            line = line.replace(w, '')
        item1.append(line)
    
    return item1

def divide_list(lista):
    #Divides list of musics
    meio = len(lista)//2
    return lista[:meio], lista[meio:]


#------------- Youtube API -------------#

def get_playlistID(yt_url):
    #Returns the youtube's playlist ID
    playlistID = yt_url.rsplit('=', 1)[1]
    return playlistID

def get_music_titles(playlistID):
    #Returns the music titles on the youtube's playlist

    api = Api(api_key=YOUTUBE_KEY)

    titles = api.get_playlist_items(playlist_id=playlistID, count= None)
    list_music = []
    for titulo in titles.items:
        musica = titulo.snippet.title.upper()

        list_music.append(musica)
    
    print(list_music)
    return list_music

def converter(access_token, user_id, yt_url, nome_playlist, descr_playlist):
  #Main process

  print(access_token)
  print(yt_url)
  playlistID = get_playlistID(yt_url)

  musicas = filter_music(get_music_titles(playlistID))

  
  id_playlist = create_playlist(access_token ,nome_playlist ,descr_playlist, user_id)
  uri_musicas = []
 

  for musica in musicas:
    uri_musicas.append(search_music(musica, access_token))

  if len(uri_musicas)>100:
    print("A DIVIDIR A LISTA")
    musicas1, musicas2 = divide_list(uri_musicas)

    musicas11 = list(filter(None, musicas1))
    musicas22 = list(filter(None, musicas2))

    print(musicas11)
    print(musicas22)

    add_music(id_playlist, musicas11, access_token)
    add_music(id_playlist, musicas22, access_token)

    musicas1.clear()
    musicas2.clear()
  else:
    print("")
    print("A playlist tem menos de 100 musicas")

    uri_musicas = list(filter(None, uri_musicas))

    add_music(id_playlist, uri_musicas, access_token)

    uri_musicas.clear()
    musicas.clear()    
