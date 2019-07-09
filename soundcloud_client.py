import soundcloud
import urllib.request

class SoundcloudClient:
	def __init__(self, _clientId, _clientSecret, _username, _password, _bpm=0, _pages=2):
		self.client = soundcloud.Client(client_id=_clientId,
			client_secret=_clientSecret,
			username=_username,
			password=_password)
		self.bpm = _bpm
		self.pages = _pages

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
		data = fname.split(" - ")
		if len(data) < 2:
			return
		from mutagen.mp3 import MP3
		from mutagen.id3 import ID3NoHeaderError
		from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC
		try: 
			tags = ID3(path)
		except ID3NoHeaderError:
			tags = ID3()
		artist = data[0].strip()
		song = data[1].strip()
		tags["TIT2"] = TIT2(encoding=3, text=song)
		#tags["TALB"] = TALB(encoding=3, text=u'Без паники')
		tags["TPE1"] = TPE1(encoding=3, text=artist)
		tags.save(path)

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