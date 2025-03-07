from typing import List, Union
from enum import IntEnum
from utils import log, LogLevel

_HAS_MUSIC_TAG_LIB = False
try:
	import music_tag
	_HAS_MUSIC_TAG_LIB = True
except:
	log(LogLevel.ERROR, "music_tag lib not found")

class TrackType(IntEnum):
	LOCAL = 1
	SOUND_CLOUD = 2
	YANDEX_MUSIC = 3

class Tag:
	def __init__(self):
		self.type: TrackType = TrackType.LOCAL
		self.url: str = ''
		self.artist: str = ''
		self.album: str = ''
		self.song: str = ''
		self.fileName: str = ''
		self.year: int = 0
		self.genre: str = ''
		self.coverart: str = ''
		self.length: int = 0
		self.curLength: int = 0
		self.id: int = -1
		self.globalId: Union[str, int] = -1 #for streamings SC and YM

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

class Playlist:
	def __init__(self):
		self.name: str = ''
		self.tracks: List[Tag] = []

	def getSize(self):
		return len(self.tracks)

def getTagFromPath(path: str) -> Tag|None:
	if not _HAS_MUSIC_TAG_LIB:
		return None
	try:
		tag = music_tag.load_file(path)
	except:
		log(LogLevel.ERROR, "getTagFromPath can`t get tag", path)
		return None
	else:
		resTag = Tag()
		resTag.url = path
		resTag.artist = tag['artist']
		resTag.album = tag['album']
		resTag.song = tag['tracktitle']
		resTag.fileName = path if path != None else ""
		resTag.year = tag['year']
		resTag.genre = tag['genre']
		resTag.id = -1
		resTag.globalId = -1
	return resTag

def setTagForPath(path: str, tag: Tag):
	if not _HAS_MUSIC_TAG_LIB:
		return
	try:
		tagSong = music_tag.load_file(path)
	except:
		log(LogLevel.ERROR, "setTagForPath can`t set tag", path)
		return
	else:
		tagSong['artist'] = tag.artist
		tagSong['album'] = tag.album
		tagSong['tracktitle'] = tag.song
		tagSong['year'] = tag.year
		tagSong['genre'] = tag.genre
	return
