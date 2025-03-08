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
		if not self.isInit:
			return ""
		try:
			artist = self.genius.search_artist(artist, max_songs=3)
			song = artist.song(song)
			return song.lyrics
		except:
			log(LogLevel.ERROR, "lyricsgenius can`t get lyrics")
			return ""

