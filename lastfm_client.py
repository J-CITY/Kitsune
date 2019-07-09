import pylast

class Lastfm:
	def __init__(self, apikey, lang='en'):
		self.lang = lang
		self.network = pylast.LastFMNetwork(api_key=apikey)

	def getArtistBio(self, name):
		try:
			artist = self.network.get_artist(name)
		except:
			return ""
		if artist != None:
			return artist.get_bio("content", language=self.lang)
		else:
			return ""