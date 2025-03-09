# Deprecated: This API already died =(
import urllib.request
import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from core.utils import log, LogLevel
from core.tag_controller import setTagForPath
_HAS_SOUNDCLOUD_LIB = False
try:
	import soundcloud
	_HAS_SOUNDCLOUD_LIB = True
except ImportError or ModuleNotFoundError:
	log(LogLevel.ERROR, "Yandex music lib not found")

class SoundcloudClient:
	isInit = False
	def __init__(self, _clientId=None, _clientSecret=None, _username=None, _password=None, _bpm=0, _pages=2):
		if not _HAS_SOUNDCLOUD_LIB:
			return
		if _clientId is None:
			return
		self.client = soundcloud.Client(client_id=_clientId,
			client_secret=_clientSecret,
			username=_username,
			password=_password)
		self.bpm = _bpm
		self.pages = _pages
		self.isInit = True

	def isInitial(self) -> bool:
		return self.isInit

	def getFavorites(self):
		if not self.isInitial():
			return None
		return self.client.get('/me/favorites')

	def getStreamByUrl(self, stream_url):
		if not self.isInitial():
			return None
		return self.client.get(stream_url, allow_redirects=False)

	def getSongUrlById(self, id):
		if not self.isInitial():
			return None
		return self.client.get('/tracks/' + str(id))

	def download(self, url, track):
		if not self.isInitial():
			return
		urllib.request.urlretrieve(url.location, track.title)

	def downloadName(self, url, path, track):
		if not self.isInitial():
			return
		urllib.request.urlretrieve(url, path)
		self.setID3Tag(path, track)

	#def setPresenter(self, p):
	#	self.presenter = p

	def getPlaylists(self):
		if not self.isInitial():
			return None
		return self.client.get('/me/playlists')

	def getPlaylistById(self, id):
		if not self.isInitial():
			return None
		return self.client.get('/playlists/'+str(id))

	def setID3Tag(self, path, fname):
		if not self.isInitial():
			return None
		from tag_controller import Tag
		data = fname.split(" - ")
		if len(data) < 2:
			return
		artist = data[0].strip()
		song = data[1].strip()
		tag = Tag()
		tag.artist = artist
		tag.song = song
		setTagForPath(path, tag)

	def like(self, id):
		if not self.isInitial():
			return None
		self.client.put('/me/favorites/%d' % id)

	def search(self, text):
		if not self.isInitial():
			return None
		res = []
		for i in range(self.pages):
			try:
				res.extend(self.client.get('/tracks', q=text, bpm={
					'from': self.bpm
				}, offset=i*10))
			except:
				break
		return res
