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
	def __init__(self, apikey = None, lang='en', cacheFolder='cache'):
		if apikey is None or _HAS_LASTFM_LIB == False:
			return
		self.lang = lang
		self.network = pylast.LastFMNetwork(api_key=apikey)
		self.isInit = True
		self.cacheFolder = cacheFolder

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
			res = artist.get_bio("content", language=self.lang)
			if res:
				return res
			return ""
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

	def getArtistImageUrl(self, artist):
		if not self.isInit:
			return None
		try:
			search = self.network.search_for_artist(artist)
			results = search.get_next_page()
			if len(results) > 0:
				images = results[0].info["image"]
				return images[pylast.SIZE_EXTRA_LARGE]
		except:
			pass
		return None

	def saveAlbumArt(self, artist, album):
		if not self.isInit:
			return ''
		url = self.getAlbumImageUrl(artist, album)
		if url is None:
			return ''
		path = os.path.join(self.cacheFolder, artist + '_' + album + '_album.png')
		urllib.request.urlretrieve(url, path)
		return path

	def saveArtistImage(self, artist):
		if not self.isInit:
			return ''
		url = self.getArtistImageUrl(artist)
		if url is None:
			return ''
		path = os.path.join(self.cacheFolder, artist + '_info.png')
		urllib.request.urlretrieve(url, path)
		return path
	
	def getTrackWiki(self, artist, song):
		if not self.isInit:
			return ""
		try:
			song = self.network.get_track(artist, song)
		except:
			return ""
		if song != None:
			res = song.get_wiki_content()
			if res:
				return res
			return ""
		else:
			return ""