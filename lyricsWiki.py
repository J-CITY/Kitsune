import lyricsgenius
class LyricsWiki:
	isInit = False
	def __init__(self, apikey=None):
		if apikey is None:
			return
		self.genius = lyricsgenius.Genius(apikey)
		self.isInit = True

	def isInitial(self) -> bool:
		return self.isInit

	def getLyrics(self, artist: str, song: str):
		artist = self.genius.search_artist(artist, max_songs=3)
		song = artist.song(song)
		return song.lyrics
		try:
			artist = self.genius.search_artist(artist)
			song = artist.song(song)
			return song.lyrics
		except:
			return ""
