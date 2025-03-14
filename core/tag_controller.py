import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from typing import List, Union
from enum import IntEnum
from core.utils import log, LogLevel

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
		self.ymCoverUrl = None
		self.ymHasLyrics = False

	def get(self, param):
		return {
			'type': self.type,
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
			'globalId': self.globalId,
			'ymCoverUrl': self.ymCoverUrl,
			'ymHasLyrics': self.ymHasLyrics
		}[param]

class Playlist:
	def __init__(self):
		self.name: str = ''
		self.tracks: List[Tag] = []

	def getSize(self):
		return len(self.tracks)

def tag_class_to_dict(obj):
	#print("{serializer hook, converting to dict: %s}" % obj)
	return {
		"__class__": "core.tag_controller.Tag",
		'type': obj.type,
		'url': obj.url,
		'artist': obj.artist,
		'album': obj.album,
		'song': obj.song,
		'fileName': obj.fileName,
		'year': obj.year,
		'genre': obj.genre,
		'coverart': obj.coverart,
		'length': obj.length,
		'curLength': obj.curLength,
		'id': obj.id,
		'globalId': obj.globalId,
		'ymCoverUrl': obj.ymCoverUrl,
		'ymHasLyrics': obj.ymHasLyrics
	}

def tag_dict_to_class(classname, d):
	#print("{deserializer hook, converting to class: %s}" % d)
	p = Tag()
	p.type = d['type']
	p.url = d['url']
	p.artist = d['artist']
	p.album = d['album']
	p.song = d['song']
	p.fileName = d['fileName']
	p.year = d['year']
	p.genre = d['genre']
	p.coverart = d['coverart']
	p.length = d['length']
	p.curLength = d['curLength']
	p.id = d['id']
	p.globalId = d['globalId']
	p.ymCoverUrl = d['ymCoverUrl']
	p.ymHasLyrics = d['ymHasLyrics']
	return p

def playlist_class_to_dict(obj):
	#print("{serializer hook, converting to dict: %s}" % obj)
	return {
		"__class__": "core.tag_controller.Playlist",
		"name": obj.name,
		"tracks": obj.tracks
	}

def playlist_dict_to_class(classname, d):
	#print("{deserializer hook, converting to class: %s}" % d)
	p = Playlist()
	p.name = d["name"]
	for e in d["tracks"]:
		p.tracks.append(tag_dict_to_class("core.tag_controller.Tag", e))
	return p

def getTagFromPath(path: str) -> Tag|None:
	if not _HAS_MUSIC_TAG_LIB:
		log(LogLevel.ERROR, "getTagFromPath lib 'music_tag' not installed")
		return None
	try:
		tag = music_tag.load_file(path)
	except:
		log(LogLevel.ERROR, "getTagFromPath can`t get tag", path)
		return None
	else:
		resTag = Tag()
		resTag.url = path
		for i, artist in enumerate(tag['artist'].values):
			if i != 0:
				resTag.artist += ","
			resTag.artist += artist
		resTag.album = str(tag['album'])
		resTag.song = str(tag['tracktitle'])
		resTag.fileName = path if path != None else ""
		resTag.year = str(tag['year'])
		resTag.genre = str(tag['genre'])
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



def savePlaylist(playlist: Playlist, path: str):
	import json
	saveList = []
	for i, t in enumerate(playlist.tracks):
		_t = {
			'url': t.url,
			'artist': t.artist if t.artist != None else "",
			'album': t.album if t.album != None else "",
			'song': t.song if t.song != None else "",
			'fileName': t.fileName if t.fileName != None else "",
			'year': t.year if t.year != None else "",
			'genre': t.genre if t.genre != None else "",
			'coverart': t.coverart if t.coverart != None else "",
			'length': t.length if t.length != None else 0,
			'curLength': t.curLength if t.curLength != None else 0,
			'id': i,
			'globalId': t.globalId,
			"type": int(t.type),
			"ymCoverUrl": t.ymCoverUrl if t.ymCoverUrl != None else '',
			"ymHasLyrics": t.ymHasLyrics,
		}
		#print(_t)
		saveList.append(_t)

	outfile = open(path, 'w')
	json.dump({'name': playlist.name, 'pl': saveList}, outfile)

def loadPlaylist(path: str) -> Playlist:
	import json
	from collections import namedtuple

	log(LogLevel.INFO, "Load playlist", path)
	try:
		f = open(path, 'r')
	except IOError as e:
		log(LogLevel.ERROR, "Load playlist fail", path)
		return Playlist()
	else:
		data = f.read()
		#print(data)
		jspl = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

		res = []
		for e in jspl.pl:
			#print(e)
			t = Tag()
			t.url = e.url
			t.artist = e.artist
			t.album = e.album
			t.song = e.song
			t.fileName = e.fileName
			t.year = e.year
			t.genre = e.genre
			t.coverart = e.coverart
			t.length = e.length
			t.curLength = e.curLength
			t.id = e.id
			t.globalId = e.globalId
			t.ymCoverUrl = e.ymCoverUrl if e.ymCoverUrl != '' else None,
			t.ymHasLyrics = e.ymHasLyrics,
			t.type = TrackType(e.type)
			res.append(t)

		playlist = Playlist()
		playlist.name = jspl.name
		playlist.tracks = res
		playlist.size = len(res)
		return playlist
