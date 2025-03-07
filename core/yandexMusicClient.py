#!/usr/bin/env python3
#import argparse
#import re
#import sys
#from pathlib import Path
#from subprocess import call
#from time import sleep
#from typing import List

from utils import log, LogLevel

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

	#def setPresenter(self, p):
	#	self.presenter = p

	def getFavorite(self):
		if not self.isInit:
			return None
		return self.client.users_likes_tracks()
	
	def getPlaylists(self):
		if not self.isInit:
			return None
		return self.client.users_playlists_list()

	def getPlaylist(self, name):
		if not self.isInit:
			return None
		playlists = self.getPlaylists()
		playlist = next((p for p in playlists if p.title == name), None)
		if playlist is None:
			print(f'playlist "{name}" not found')
			return []
		return playlist.tracks if playlist.tracks else playlist.fetch_tracks()

	def getWorldChart(self):
		if not self.isInit:
			return None
		return self.client.chart('world').chart
	
	def getTrack(self, id):
		if not self.isInit:
			return None
		return self.client.tracks(id)[0]
	
	def getTracks(self, ids):
		if not self.isInit:
			return None
		return self.client.tracks(ids)

	def getTrackUrl(self, id):
		if not self.isInit:
			return None
		track = self.client.tracks(id)[0]
		info = track.get_specific_download_info("mp3", 192)
		if info:
			return info.get_direct_link()
		return None
