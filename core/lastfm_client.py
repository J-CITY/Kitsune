import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

import urllib.request
from core.utils import log, LogLevel

_HAS_LASTFM_LIB = False
try:
	import pylast
	_HAS_LASTFM_LIB = True
except ImportError or ModuleNotFoundError:
	log(LogLevel.ERROR, "pylast lib not found")

class Lastfm:
	isInit = False
	def __init__(self, apikey = None, lang='en'):
		if apikey is None or _HAS_LASTFM_LIB == False:
			return
		self.lang = lang
		self.network = pylast.LastFMNetwork(api_key=apikey)
		self.isInit = True

	def isInitial(self) -> bool:
		return self.isInit
	
	#def setPresenter(self, p):
	#	self.presenter = p

	def getArtistBio(self, name):
		if not self.isInit:
			return ""
		try:
			artist = self.network.get_artist(name)
		except:
			return ""
		if artist != None:
			return artist.get_bio("content", language=self.lang)
		else:
			return ""

	def getAlbumImageUrl(self, artist, album):
		if not self.isInit:
			return None
		try:
			_album = self.network.get_album(artist, album)
		except:
			return None
		if _album != None:
			return _album.get_cover_image(2)
		else:
			return None

	def saveAlbumArt(self, artist, album):
		if not self.isInit:
			return False
		if self.presenter == None:
			return False
		url = self.getAlbumImageUrl(artist, album)
		if url is None:
			return False

		path = self.presenter.config.cash_folder

		#with open(path + '/album.png', 'wb') as handle:
		urllib.request.urlretrieve(url, path + '/album.png')

		#if os.name == OS_WIN:
		#	img = Image.open(path + '/album.png')
		#	img.save(path + '/album.ico')
		return True