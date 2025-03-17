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

	def getAlbums(self):
		self.client.albums_with_tracks
		if not self.isInit:
			return None
		result = self.client.users_likes_albums()
		playlists = []
		for p in result:
			playlist = {"title": p.album.title, "tracks": []}
			albumWithTracks = p.album.with_tracks()
			for songList in albumWithTracks.volumes:
				for song in songList:
					playlist["tracks"].append(song.id)
			playlists.append(playlist)
		return playlists

	def _getAlbums(self):
		if not self.isInit:
			return None
		return self.client.users_likes_albums()

	def getAlbum(self, name):
		if not self.isInit:
			return None
		playlists = self._getAlbums()
		playlist = next((p for p in playlists if p.album.title == name), None)
		if playlist is None:
			log(LogLevel.ERROR, f'Yandex music album "{name}" not found')
			return []

		#self.client.albums_with_tracks

		_playlist = {"title": name, "tracks": []}
		albumWithTracks = playlist.album.with_tracks()
		for songList in albumWithTracks.album.volumes:
			for song in songList:
				_playlist["tracks"].append(song.id)

		return _playlist

	def getAlbumById(self, id):
		if not self.isInit:
			return None

		playlist = self.client.albums_with_tracks(id)
		if playlist is None:
			return None

		_playlist = {"title": playlist.title, "tracks": []}
		for songList in playlist.volumes:
			for song in songList:
				_playlist["tracks"].append(song.id)

		return _playlist

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

	def getPlaylistById(self, id):
		if not self.isInit:
			return None

		playlist = self.client.playlists_list(id)
		if playlist is None:
			return None

		tracksResult = playlist[0].tracks if playlist[0].tracks else playlist[0].fetch_tracks()
		tracks = []
		for t in tracksResult:
			tracks.append(t.id)
		_playlist = {"title": playlist[0].title, "tracks": tracks}
		return _playlist

	def getAlbum(self, id):
		if not self.isInit:
			return None

		album = self.client.albums_with_tracks(id)
		if album is None:
			return None

		tracksResult = []
		for v in album.volumes:
			tracksResult += v
		tracks = []
		for t in tracksResult:
			tracks.append({'id': t.id, 'title': t.title})
		return {"title": album.title, "tracks": tracks}

	def getArtist(self, id):
		if not self.isInit:
			return None

		albums = self.client.artists_direct_albums(id)
		if albums is None:
			return None

		albums = []
		for t in albums:
			albums.append({'id': t.id, 'title': t.title})
		return {"albums": albums}

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

	def getChart(self, name):
		if not self.isInit:
			return None
		result = self.client.chart(name).chart
		if result is None:
			return None
		playlist = {"name": name, "tracks": []}
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
		result = self.client.tracks_lyrics(id)
		if result:
			return result.fetch_lyrics()
		print("YM lyrics not found")
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

	def search(self, query):
		if not self.isInit:
			return None
		searchResult = self.client.search(query)
		type_ = searchResult.best.type
		best_ = searchResult.best.result

		result = {}
		if best_:
			best = {}
			best['type'] = type_
			if type_ == 'track':
				best['id'] = best_.id
				best['artists'] = [a.name for a in best_.artists]
				best['albums'] = [a.name for a in best_.albums]
				best['title'] = best_.title
			elif type_ == 'artist':
				best['id'] = best_.id
				best['artist'] = best_.name
			elif type_ == 'album':
				best['id'] = best_.id
				best['album'] = best_.title
			elif type_ == 'playlist':
				best['id'] = best_.id
				best['playlist'] = best_.title
			result['best'] = best

		result['artists'] = self._getArtists(searchResult)
		result['albums'] = self._getAlbums(searchResult)
		result['tracks'] = self._getTracks(searchResult)
		result['playlists'] = self._getPlaylistsSearch(searchResult)
		return result

	def _getArtists(self, searchResult):
		if not self.isInit:
			return None
		if searchResult.artists:
			artists = []
			for artist in searchResult.artists.results:
				artists.append({'id': artist.id, 'name': artist.name})
			return artists

	def _getAlbums(self, searchResult):
		if searchResult.albums:
			albums = []
			for album in searchResult.albums.results:
				albums.append({'id': album.id, 'name': album.name})
			return albums

	def _getTracks(self, searchResult):
		if searchResult.tracks:
			tracks = []
			for track in searchResult.tracks.results:
				tracks.append({'id': track.id, 'name': track.name})
			return tracks

	def _getPlaylistsSearch(self, searchResult):
		if searchResult.playlists:
			playlists = []
			for playlist in searchResult.playlists.results:
				playlists.append({'id': playlist.id, 'name': playlist.name})
			return playlists

	def searchArtist(self, query):
		if not self.isInit:
			return None
		searchResult = self.client.search(query)
		result = {}
		result['artists'] = self._getArtists(searchResult)
		return result

	def searchArtist(self, query):
		if not self.isInit:
			return None
		searchResult = self.client.search(query)
		result = {}
		result['albums'] = self._getAlbums(searchResult)
		return result

	def searchSong(self, query):
		if not self.isInit:
			return None
		searchResult = self.client.search(query)
		result = {}
		result['tracks'] = self._getTracks(searchResult)
		return result

	def searchPlaylists(self, query):
		if not self.isInit:
			return None
		searchResult = self.client.search(query)
		result = {}
		result['playlists'] = self._getPlaylistsSearch(searchResult)
		return result

