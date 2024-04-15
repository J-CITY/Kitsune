from typing import List, Union
from enum import IntEnum

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
		self.size: int = 0
		self.tracks: List[Tag] = []


def getTagFromPath(path: str) -> Tag:
	import music_tag
	try:
		tag = music_tag.load_file(path)
	except:
		return Tag()
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
	import music_tag
	try:
		tagSong = music_tag.load_file(path)
	except:
		return
	else:
		tagSong['artist'] = tag.artist
		tagSong['album'] = tag.album
		tagSong['tracktitle'] = tag.song
		tagSong['year'] = tag.year
		tagSong['genre'] = tag.genre
	return
