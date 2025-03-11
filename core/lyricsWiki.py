import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from core.utils import log, LogLevel

_HAS_LIRICS_LIB = False
try:
	import lyricsgenius
	_HAS_LIRICS_LIB = True
except ImportError or ModuleNotFoundError:
	log(LogLevel.ERROR, "lyricsgenius lib not found")

def extractLyrics(artist, song):
	import json
	import requests
	link = 'https://api.lyrics.ovh/v1/'+artist.replace(' ', '%20')+'/'+song.replace(' ', '%20')
	req = requests.get(link)
	json_data = json.loads(req.content)
	try:
		lyrics = json_data['lyrics']
		#print(lyrics)
		return lyrics
	except:
		#print("Sont not found")
		return ""

class LyricsWiki:
	isInit = False
	def __init__(self, apikey=None):
		if apikey is None or _HAS_LIRICS_LIB == False:
			return
		self.genius = lyricsgenius.Genius(apikey)
		self.isInit = True

	def isInitial(self) -> bool:
		return self.isInit

	def getLyrics(self, artist: str, song: str):
		#songs = self.genius.search_songs(artist + " " + song)["hits"]
		#for s in songs:
		#	if s['result']['title'] == song:
		#		song_id = s['result']['id']
		#		return self.genius.lyrics(song_id)
		return extractLyrics(artist, song)

