import pylast
import urllib.request
from strings import OS_WIN, OS_LINUX
import os
#if os.name == OS_WIN:
#	from PIL import Image

class Lastfm:
	def __init__(self, apikey, lang='en'):
		self.lang = lang
		self.network = pylast.LastFMNetwork(api_key=apikey)

	def setPresenter(self, p):
		self.presenter = p

	def getArtistBio(self, name):
		try:
			artist = self.network.get_artist(name)
		except:
			return ""
		if artist != None:
			return artist.get_bio("content", language=self.lang)
		else:
			return ""

	def getAlbumImageUrl(self, artist, album):
		try:
			_album = self.network.get_album(artist, album)
		except:
			return ""
		if _album != None:
			return _album.get_cover_image(2)
		else:
			return ""

	def saveAlbumArt(self, artist, album):
		if self.presenter == None:
			return False
		url = self.getAlbumImageUrl(artist, album)
		if url == "":
			return False

		path = self.presenter.config.cash_folder

		#with open(path + '/album.png', 'wb') as handle:
		urllib.request.urlretrieve(url, path + '/album.png')

		#if os.name == OS_WIN:
		#	img = Image.open(path + '/album.png')
		#	img.save(path + '/album.ico')
		return True