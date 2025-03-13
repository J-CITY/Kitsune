#!/usr/bin/env python3
#import argparse
#import re
#import sys
#from pathlib import Path
#from subprocess import call
#from time import sleep
#from typing import List
import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from core.utils import log, LogLevel
from core.tag_controller import Playlist, Tag, TrackType
from core.strings import YANDEX_MUSIC_LIKES

_HAS_YANDEX_LIB = False
try:
	from yandex_music import Client
	_HAS_YANDEX_LIB = True
except ImportError or ModuleNotFoundError:
	log(LogLevel.ERROR, "Yandex music lib not found")

class YandexMusicClient:
	isInit = False
	def __init__(self, token = None) -> None:
		if not _HAS_YANDEX_LIB:
			return
		if token is None:
			return
		self.token = token
		try:
			self.client = Client(token, report_unknown_fields=False).init()
			self.isInit = True
		except:
			log(LogLevel.ERROR, "Yandex music lib not inited")

	def isInitial(self) -> bool:
		return self.isInit

	def getFavorite(self) -> Playlist:
		if not self.isInit:
			return None
		result = self.client.users_likes_tracks()
		if result is None:
			return None
		playlist = {"title": YANDEX_MUSIC_LIKES, "tracks": []}
		for i, song in enumerate(result.tracks):
			playlist["tracks"].append(song.id)
		return playlist
	
	def getPlaylists(self):
		if not self.isInit:
			return None
		result = self.client.users_playlists_list()
		playlists = []
		for p in result:
			playlist = {"title": p.title, "tracks": []}
			for i, song in enumerate(p.tracks):
				playlist["tracks"].append(song.id)
			playlists.append(playlist)
		return playlists

	def _getPlaylists(self):
		if not self.isInit:
			return None
		return self.client.users_playlists_list()

	def getPlaylist(self, name):
		if not self.isInit:
			return None
		playlists = self._getPlaylists()
		playlist = next((p for p in playlists if p.title == name), None)
		if playlist is None:
			log(LogLevel.ERROR, f'Yandex music playlist "{name}" not found')
			return []
		
		tracksResult = playlist.tracks if playlist.tracks else playlist.fetch_tracks()
		tracks = []
		for t in tracksResult:
			tracks.append(t.id)
		_playlist = {"title": name, "tracks": tracks}
		return _playlist

	def getWorldChart(self):
		if not self.isInit:
			return None
		result = self.client.chart('world').chart
		if result is None:
			return None
		playlist = {"name": 'world', "tracks": []}
		for i, song in enumerate(result.tracks):
			playlist["tracks"].append(song.id)
		return playlist
	
	def getTrack(self, id):
		if not self.isInit:
			return None
		res = self.client.tracks(id)
		if len(res) <= 0:
			return None
		s = res[0]
		song = {
			'id': s.id,
			'title': s.title,
			'artists': [artist.name for artist in s.artists],
			'albums': [album.title for album in s.albums],
			'available': s.available,
			'lyrics_available': s.lyrics_available,
			'cover_uri': s.cover_uri,
		}
		return song
	
	def getTracks(self, ids):
		if not self.isInit:
			return None
		res = self.client.tracks(ids)
		if len(res) <= 0:
			return []
		songs = []
		for s in res:
			song = {
				'id': s.id,
				'title': s.title,
				'artists': [artist.name for artist in s.artists],
				'albums': [album.title for album in s.albums],
				'available': s.available,
				'lyrics_available': s.lyrics_available,
				'cover_uri': s.cover_uri,
			}
			songs.append(song)
		
		return songs

	def getTrackUrl(self, id, bitrate=192) -> str|None:
		if not self.isInit:
			return None
		track = self.client.tracks(id)[0]
		info = track.get_specific_download_info("mp3", bitrate)
		if info:
			return info.get_direct_link()
		return None

	def downloadTrack(self, id, cacheFolder, bitrate=192):
		if not self.isInit:
			return ''
		res = self.client.tracks(id)
		if len(res) <= 0:
			return ''
		track = res[0]
		path = os.path.join(cacheFolder, track.artists[0].name + '-' + track.title + '.mp3')
		track.download(path, 'mp3', bitrate)
		return path

	def getLyrics(self, id):
		if not self.isInit:
			return ''
		result = self.client.tra(id)
		if result:
			return result.fetch_lyrics()
		return ''

	def saveCover(self, artist, album, id, cacheFolder, size: str = '200x200'):
		if not self.isInit:
			return ''
		res = self.client.tracks(id)
		if len(res) <= 0:
			return ''
		track = res[0]
		path = os.path.join(cacheFolder, artist + '_' + album + '_album.png')
		track.download_cover(path, size)
		return path

	def saveArtistImage(self, artist, id, cacheFolder, size: str = '200x200'):
		if not self.isInit:
			return ''
		res = self.client.tracks(id)
		if len(res) <= 0:
			return ''
		track = res[0]
		artist = track.artists[0]
		path = os.path.join(cacheFolder, artist + '_info.png')
		artist.download_op_image(path, size)
		return path
