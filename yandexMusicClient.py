#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from subprocess import call
from time import sleep
from typing import List

from yandex_music import Client

class YandexMusicClient:
	isInit = False
	def __init__(self, token = None) -> None:
		if token is None:
			return
		self.token = token
		self.client = Client(token, report_unknown_fields=False).init()
		self.isInit = True

	def isInitial(self) -> bool:
		return self.isInit

	def setPresenter(self, p):
		self.presenter = p

	def getFavorite(self):
		return self.client.users_likes_tracks()
	
	def getPlaylists(self):
		return self.client.users_playlists_list()

	def getPlaylist(self, name):
		playlists = self.getPlaylists()
		playlist = next((p for p in playlists if p.title == name), None)
		if playlist is None:
			print(f'playlist "{name}" not found')
			return []
		return playlist.tracks if playlist.tracks else playlist.fetch_tracks()

	def getWorldChart(self):
		return self.client.chart('world').chart
	
	def getTrack(self, id):
		return self.client.tracks(id)[0]
	
	def getTracks(self, ids):
		return self.client.tracks(ids)

	def getTrackUrl(self, id):
		track = self.client.tracks(id)[0]
		info = track.get_specific_download_info("mp3", 192)
		if info:
			return info.get_direct_link()
		return None
