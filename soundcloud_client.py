import soundcloud
import urllib.request

class SoundcloudClient:
	isInit = False
	def __init__(self, _clientId=None, _clientSecret=None, _username=None, _password=None, _bpm=0, _pages=2):
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
		return self.client.get('/me/favorites')

	def getStreamByUrl(self, stream_url):
		return self.client.get(stream_url, allow_redirects=False)

	def getSongUrlById(self, id):
		return self.client.get('/tracks/' + str(id))

	def download(self, url, track):
		urllib.request.urlretrieve(url.location, track.title)

	def downloadName(self, url, path, track):
		urllib.request.urlretrieve(url, path)
		self.setID3Tag(path, track)

	def setPresenter(self, p):
		self.presenter = p

	def getPlaylists(self):
		return self.client.get('/me/playlists')

	def getPlaylistById(self, id):
		return self.client.get('/playlists/'+str(id))

	def setID3Tag(self, path, fname):
		from tag_controller import Tag
		data = fname.split(" - ")
		if len(data) < 2:
			return
		artist = data[0].strip()
		song = data[1].strip()
		tag = Tag()
		tag.artist = artist
		tag.song = song
		self.presenter.saveSongsMetadatas(path, tag)

	def like(self, id):
		self.client.put('/me/favorites/%d' % id)

	def search(self, text):
		res = []
		for i in range(self.pages):
			try:
				res.extend(self.client.get('/tracks', q=text, bpm={
					'from': self.bpm
				}, offset=i*10))
			except:
				break
		return res