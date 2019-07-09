from PyLyrics import *

class LyricsWiki:
	def __init__(self):
		pass

	def getLyrics(self, artist, song):
		try:
			return PyLyrics.getLyrics(artist, song)
		except:
			return ""