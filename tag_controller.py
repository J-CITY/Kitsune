from tinytag import TinyTag

class Tag:
	def __init__(self):
		self.url = ''
		self.artist = ''
		self.album = ''
		self.song = ''
		self.fileName = ''
		self.year = 0
		self.genre = ''
		self.coverart = ''
		self.length = 0
		self.curLength = 0
		self.id = -1
		self.globalId = -1

	def get(self, param):
		return {
			'url': self.url,
			'artist': self.artist,
			'album': self.album,
			'song': self.song,
			'fileName': self.fileName,
			'year': self.year,
			'genre': self.genre,
			'coverart': self.coverart,
			'length': self.length,
			'curLength': self.curLength,
			'id': self.id,
			'globalId': self.globalId
		}[param]

def getTagFromPath(path):
	try:
		tag = TinyTag.get(path)
	except:
		return Tag()
	else:
		resTag = Tag()
		resTag.url = path
		resTag.artist = tag.artist if tag.artist != None else ""
		resTag.album = tag.album if tag.album != None else ""
		resTag.song = tag.title if tag.title != None else ""
		resTag.fileName = path if path != None else ""
		resTag.year = tag.year if tag.year != None else ""
		resTag.genre = tag.genre if tag.genre != None else ""
		resTag.id = -1
		resTag.globalId = -1
	return resTag


