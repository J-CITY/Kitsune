import threading, time, os
from Pyro5.api import expose, callback, Daemon, Proxy
from Pyro5.api import register_dict_to_class, register_class_to_dict
from core.utils import MusicAddPolitics
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from core.db import *
from gui.utils.widget import CustomFrame
import threading, asyncio
from enum import Enum
from typing import NoReturn, Dict, Optional
from core.tag_controller import Tag, Playlist, getTagFromPath, setTagForPath, playlist_class_to_dict, playlist_dict_to_class
from core.strings import *
from core.locale import LocaleConfig
from core.keyboard import Keyboard

PLAYLIST_CURRENT = 'current'

NEED_UPDATE_SONG_TAG = False

class CallbackHandler(object):
	def __init__(self):
		self.presenter = None

	@expose
	@callback
	def default(self):
		pass

class Request:
	def __init__(self, type, payload, callback):
		self.type = type
		self.callback = callback
		self.payload = payload

requestsQueue = []

class ReuestEnum:
	YM_GET_FAVORITES = 0
	GET_LYRICS = 1
	LOAD_COVER = 2
	GET_ARTISI_BIO = 3
	SEARCH_YM_TRACKS = 4
	LOAD_YM_PLAYLIST = 5

class Presenter:
	def __init__(self, config):#+
		self.config = config
		# str -> frame
		self.frames = {}
		# Available frames in a specific order
		self.framesOrder = []

		self.song = None
		self.playlistsCash: Dict[str, Playlist] = {}

		#init daemon client
		self.daemon = Daemon()
		self.callbackHandler = CallbackHandler()
		self.callbackHandler.presenter = self
		self.daemon.register(self.callbackHandler)
		
		self.server = Proxy("PYRONAME:kitsune.music.daemon")

		register_class_to_dict(Playlist, playlist_class_to_dict)
		register_dict_to_class("core.tag_controller.Playlist", playlist_dict_to_class)
		register_class_to_dict(Tag, tag_class_to_dict)
		register_dict_to_class("core.tag_controller.Tag", tag_dict_to_class)

		self.useInternet = self.server.getUseInternet()
		self.musicRootFolder = self.server.getMusicRootDir()
		self.downloadFolder = self.server.getDownloadDir()
		self.playlistFolder = self.server.getPlaylistDir()

		self.locale = LocaleConfig(self.config)
		self.keyboard = Keyboard(self.config)

	def getUseInternet(self):
		return self.useInternet
	
	def getPlaylistFolder(self):
		return self.playlistFolder

	def getMusicRootFolder(self):
		return self.musicRootFolder

	def getDownloadFolder(self):
		return self.downloadFolder

	def tryGetPlaylist(self, name: str) -> Playlist|None:#+
		if name in self.playlistsCash:
			return self.playlistsCash[name]
		return None

	def setUpBar(self, w):#+
		self.upBar = w

	def setDownBar(self, w):#+
		self.downBar = w

	def addFrame(self, id: str, frame: CustomFrame) -> NoReturn:#+
		self.frames[id] = frame

	def dbSelect(self, query):#+
		return self.server.dbSelect(query)

	def dbSearch(self, text):#+
		return self.server.dbSearch(text)

	def dbExecute(self, text, params):#+
		return self.server.dbExecute(text, params)

	def dbInsertByPath(self, path):#+
		self.server.dbInsertByPath(path)

	def playerGetCurTag(self):#+
		return self.server.playerGetCurrentTag()

	def playerPlayById(self, id):#+
		self.song = self.server.playerPlayById(id)

	def playerPlay(self, song):#+
		tag = getTagFromPath(song)
		if tag is None:
			log(LogLevel.ERROR, "Presenter.playerPlay: cant get tag", song)
			return
		tag.length = self.server.playerGetSongLength()
		self.song = tag
		#self.player.playlist.tracks = [tag]
		self.server.playerSetCurrentPlaylistTracks([tag])
		self.server.play()

	def playerStop(self):#+
		self.server.stop()

	def playerSwap(self, _from, _to):#+
		if _from == _to:
			return
		self.server.playerSwap(_from, _to)
		self.frames[FRAME_MAIN_PLAYLIST].table.updateList(self.server.playerGetPlaylist().tracks)

	def playerDelete(self, id):#+
		self.server.playerDelete(id)
		self.frames[FRAME_MAIN_PLAYLIST].table.updateList(self.server.playerGetPlaylist().tracks)
	
	def playlistAddPlaylist(self, pos, isPlay, name):#+
		spl = self.frames[FRAME_PLAYLISTS].curPlaylist
		if pos == MusicAddPolitics.ADD_END or pos == MusicAddPolitics.ADD_BEFORE:
			for e in spl.tracks:
				self.mainPlaylistAddSong(pos, isPlay, name, e)
				isPlay = False
		else:
			lenpl = len(spl)
			_isPlay = False
			for e in reversed(spl.tracks):
				lenpl-=1
				if lenpl == 0:
					_isPlay = isPlay
				self.mainPlaylistAddSong(pos, _isPlay, name, e)
	
	def medialibAddAlbum(self, pos, isPlay, name):#+
		spl = self.medialibGetCurrentAlbum()
		if pos == MusicAddPolitics.ADD_END or pos == MusicAddPolitics.ADD_BEFORE:
			for e in spl.tracks :
				self.mainPlaylistAddSong(pos, isPlay, name, e)
				isPlay = False
		else:
			lenpl = len(spl)
			_isPlay = False
			for e in reversed(spl.tracks):
				lenpl-=1
				if lenpl == 0:
					_isPlay = isPlay
				self.mainPlaylistAddSong(pos, _isPlay, name, e)

	def medialibUpdate(self):#+
		self.frames[FRAME_MEDIALIB].updateMl()

	def playlistAddSong(self, pos, isPlay, name):#+
		e = self.frames[FRAME_PLAYLISTS].curPlaylist.tracks[self.frames[FRAME_PLAYLISTS].listPl._line]
		self.mainPlaylistAddSong(pos, isPlay, name, e)

	def mainPlaylistUpdateList(self):#+
		self.frames[FRAME_MAIN_PLAYLIST].table.updateList(self.server.playerGetPlaylist().tracks)
	
	def mainPlaylistOpen(self, pl):#+
		for i, p in enumerate(pl):
			p.id = i
		self.server.playerSetCurrentPlaylistTracks(pl)
		self.frames[FRAME_MAIN_PLAYLIST].table.updateList(pl)
		self.frames[FRAME_MAIN_PLAYLIST].table.value = 0
		self.frames[FRAME_MAIN_PLAYLIST].table._line = 0

	def medialibCreateNewPlaylistAndSaveSong(self, playlistName):
		path = os.path.join(self.config.playlist_folder, playlistName)
		song = self.medialibGetCurrentTag()
		song.id = 0
		savePlaylist([song], path)
		self.playlistsUpdatePlaylists()

	def medialibAddSong(self, pos, isPlay, name):#+
		e = self.medialibGetCurrentTag()
		self.mainPlaylistAddSong(pos, isPlay, name, e)

	def searchAddSong(self, pos, isPlay, name):
		e = self.frames[FRAME_SEARCH].getCurTag()
		if e != None:
			self.mainPlaylistAddSong(pos, isPlay, name, e)

	def medialibGetCurrentTag(self):#+
		return self.frames[FRAME_MEDIALIB].getCurrentTag()

	def mainPlaylistAddSong(self, addParam, needPlay: bool, playlistName: str, _tag=None):#+
		if _tag == None:
			log(LogLevel.ERROR, "mainPlaylistAddSong: _tag in None")
			return

		tag = _tag
		if len(self.frames[FRAME_MAIN_PLAYLIST].table._options) > 0 and self.frames[FRAME_MAIN_PLAYLIST].table._line < 0:
			self.frames[FRAME_MAIN_PLAYLIST].table._line = 0

		if playlistName == PLAYLIST_CURRENT:
			playlist = self.server.playerGetPlaylist()
		else:
			path = os.path.join(self.config.playlist_folder, playlistName)
			playlist = loadPlaylist(path)

		if addParam == MusicAddPolitics.ADD_END:
			tag.id = len(playlist.tracks)
			playlist.tracks.append(tag)
		elif addParam == MusicAddPolitics.ADD_BEGIN:
			tag.id = 0
			playlist.tracks = [tag] + playlist.tracks
			for e in playlist.tracks[1:]:
				e.id+=1
		elif addParam == MusicAddPolitics.ADD_AFTER:
			tag.id = self.frames[FRAME_MAIN_PLAYLIST].getCurrentLineId()+1 if playlistName == PLAYLIST_CURRENT else 0
			if tag.id == len(playlist.tracks):
				playlist.tracks = playlist.tracks[0:tag.id]+[tag]
			else:
				playlist.tracks = playlist.tracks[0:tag.id]+[tag]+playlist.tracks[tag.id:]
			for e in playlist.tracks[tag.id+1:]:
				e.id+=1
		elif addParam == MusicAddPolitics.ADD_BEFORE:
			tag.id = self.frames[FRAME_MAIN_PLAYLIST].getCurrentLineId() if playlistName == PLAYLIST_CURRENT else 0
			if tag.id == 0:
				playlist.tracks = [tag]+playlist.tracks[tag.id:]
			else:
				playlist.tracks = playlist.tracks[0:tag.id]+ [tag]+playlist.tracks[tag.id:]
			for e in playlist.tracks[tag.id+1:]:
				e.id+=1

		if playlistName == PLAYLIST_CURRENT:
			self.server.playerSetCurrentPlaylistTracks(playlist.tracks)
			self.song = tag
			self.frames[FRAME_MAIN_PLAYLIST].table.updateList(playlist.tracks)
			if needPlay:
				self.mainPlaylistSetPlayId(tag.id)
		else:
			savePlaylist(playlist.tracks, path)
			self.playlistsUpdatePlaylists()

	def browserCreateNewPlaylistAndSaveSong(self, playlistName):#+
		frame = self.frames.get(FRAME_BROWSER, None)
		if frame is None:
			log(LogLevel.INFO, "Presenter.browserCreateNewPlaylistAndSaveSong: 'BrowserFrame' doesn`t exist")
			return

		pathPlaylist = os.path.join(self.config.playlist_folder, playlistName)
		song = self.frames[FRAME_BROWSER].browser.value
		tag = getTagFromPath(song)
		if tag is None:
			log(LogLevel.ERROR, "Presenter.browserCreateNewPlaylistAndSaveSong: cant get tag", song)
			return
		tag.length = self.player.getLen()
		tag.id = 0
		savePlaylist([tag], pathPlaylist)
		self.playlistsUpdatePlaylists()

	def mainPlaylistSetPlayId(self, id):#+
		self.frames[FRAME_MAIN_PLAYLIST].table.playId = id
		self.playerPlayById(id)

	def barUpdate(self):#+
		localserver = Proxy("PYRONAME:kitsune.music.daemon")
		while True:
			tag = localserver.playerGetCurrentTagWithLength()
			self.frames[FRAME_MAIN_PLAYLIST].table.playId = tag.id
			self.song = tag
			self.mainPlaylistUpdateCover()
			#print(self.song)
			if self.song != None:
				tag = {
					'url': self.song.url,
					'artist': self.song.artist,
					'album': self.song.album,
					'song': self.song.song,
					'fileName': self.song.fileName,
					'year': str(self.song.year),
					'genre': self.song.genre,
					'coverart': self.song.coverart,
					'length': int(self.song.length),
					'curLength': int(self.song.curLength),
					'id': str(self.song.id),
					'volume': str(int(localserver.getVolume())),
					'maxVolume': str(100),
					'mode': localserver.getMode(),
					'crossfade': localserver.getCrosfade(),
				}

				#if localserver.playerGetIsPlay():
				tag['length'] = int(localserver.playerGetSongLength())
				tag['curLength'] = int(localserver.playerGetCurrentSongProgress())
				self.upBar.update(tag)
				self.downBar.update(tag)
			time.sleep(.200)

	def run(self):#+
		thread = threading.Thread(target=self.barUpdate)
		thread.daemon = True
		thread.start()

		#if not self.useInternet:
		#	return
		thread = threading.Thread(target=self.asyncHandler)
		thread.daemon = True
		thread.start()

	def setFrameToBars(self, fstr):#+
		frame = self.frames.get(fstr, None)
		if frame is None:
			print("Fame none", fstr)
			return
		self.upBar.setFrame(frame)
		self.downBar.setFrame(frame)

	def createNewPlaylistAndSaveMainPlaylist(self, playlistName):
		path = os.path.join(self.config.playlist_folder, playlistName)
		savePlaylist(self.player.playlist, path)
		self.playlistsUpdatePlaylists()

	def createNewPlaylistFromSearch(self, playlistName):
		path = os.path.join(self.config.playlist_folder, playlistName)
		e = self.frames[FRAME_SEARCH].getCurTag()
		if e == None:
			return
		savePlaylist([e], path)
		self.playlistsUpdatePlaylists()

	def medialibCreateNewPlaylistAlbum(self, playlistName):
		path = os.path.join(self.config.playlist_folder, playlistName)
		playlist = self.medialibGetCurrentAlbum()
		savePlaylist(playlist, path)
		self.playlistsUpdatePlaylists()

	def medialibGetCurrentAlbum(self):#+
		return self.frames[FRAME_MEDIALIB].getCurrentAlbum()

	def getListOfPlaylists(self) -> List[str]:#+
		return self.server.getListOfPlaylists()

	def getPathOfPlaylist(self, name):#+
		return os.path.join(self.config.playlist_folder, name)

	def playlistsUpdatePlaylists(self):#+
		self.frames[FRAME_PLAYLISTS].updatePlaylists()

	def playerEventControl(self, event):#+
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('p')]:
				self.server.pause()
			if event.key_code in [ord('S')]:
				self.server.stop()
			if event.key_code in [ord('>')]:
				self.server.stop()
				self.server.next()
			if event.key_code in [ord('<')]:
				self.server.stop()
				self.server.prev()
			if event.key_code in [ord('.')]:
				self.server.moveDirection(1)
			if event.key_code in [ord(',')]:
				self.server.moveDirection(-1)
			if event.key_code in [ord('-')]:
				self.server.volumeDown()
			if event.key_code in [ord('=')]:
				self.server.volumeUp()
			if event.key_code in [ord('v')]:
				self.server.mute()
			if event.key_code in [ord('b')]:
				self.server.changeMode()
			if event.key_code in [ord('c')]:
				self.server.changeCrossfade()

	def eqSetLevelParam(self, param):#+
		self.server.eqSetLevelParam(param)

	def eqSetSpeedParam(self ,param):#+
		self.server.eqSetSpeedParam(param)

	def eqSetBassParam(self, param):#+
		self.server.eqSetBassParam(param)

	def eqSetEchoParam(self, param):#+
		self.server.eqSetEchoParam(param)

	def eqSetChorusParam(self, param):#+
		self.server.eqSetChorusParam(param)

	def eqSetFlangeParam(self, param):#+
		self.server.eqSetFlangeParam(param)

	def eqSetReverbParam(self, param):#+
		self.server.eqSetReverbParam(param)

	def playerGetWaveData(self, isSterio, col):#+
		return self.server.playerGetWaveData(isSterio, col)

	def playerGetFFTData(self, isSterio, col):#+
		return self.server.playerGetFFTData(isSterio, col)

	def barGetFrameName(self):#+
		return self.upBar.getFrameName()

	def artistinfoUpdateText(self):#+
		if not self.useInternet:
			return ''
		if self.frames[FRAME_ARTIST_INFO].updateArtist() or not self.song:
			return

		r = Request(ReuestEnum.GET_ARTISI_BIO, 
			{'artist': self.song.artist}, 
			self.frames[FRAME_ARTIST_INFO].updateArtistCb)
		self.addRequest(r)

	#def lyricsUpdateTextAsync(self, artist, song, server = None):
	#	if server:
	#		localserver = server
	#	else:
	#		localserver = Proxy("PYRONAME:kitsune.music.daemon")
	#	text = localserver.lyricsGetSongLyrics(artist, song)
	#	if self.frames[FRAME_LYRICS].artist == artist and self.frames[FRAME_LYRICS].song == song:
	#		self.frames[FRAME_LYRICS].setText(text)
	#	else:
	#		self.lyricsUpdateTextAsync(self.frames[FRAME_LYRICS].artist, self.frames[FRAME_LYRICS].song, localserver)

	def lyricsUpdateText(self):#+
		if not self.useInternet:
			return
		if self.frames[FRAME_LYRICS].updateArtistSong() or not self.song:
			return
		r = Request(ReuestEnum.GET_LYRICS, 
			{'artist': self.song.artist, 'song': self.song.song, 'ymId': None if self.song.globalId == -1 else self.song.globalId }, 
			self.frames[FRAME_LYRICS].updateLyricsCb)
		self.addRequest(r)

	def lyricsUpdateCover(self):#+
		if not self.useInternet:
			return
		if self.frames[FRAME_LYRICS].updateCover():
			return
		r = Request(ReuestEnum.LOAD_COVER, 
			{'artist': self.song.artist, 'album': self.song.album, 'ymId': self.song.globalId if self.song.globalId != -1 else None}, 
			self.frames[FRAME_LYRICS].updateCoverCb)
		self.addRequest(r)

	def mainPlaylistUpdateCover(self):#+
		if not self.useInternet:
			return
		if self.frames[FRAME_MAIN_PLAYLIST].updateCover():
			return
		r = Request(ReuestEnum.LOAD_COVER, 
			{'artist': self.song.artist, 'album': self.song.album, 'ymId': self.song.globalId if self.song.globalId != -1 else None}, 
			self.frames[FRAME_MAIN_PLAYLIST].updateCoverCb)
		self.addRequest(r)

	def playerGetLen(self):#+
		return self.server.playerGetSongLength()

	def playerGetBuf(self):#+
		return self.server.playerGetCurrentSongProgress()

	def getYandexMusicFavorites(self):#+
		return self.server.yandexMusicGetFavorites()

	def getYandexMusicPlaylists(self):#+
		return self.server.yandexMusicGetPlaylists()
	
	def getYandexMusicPlaylist(self, name):#+
		return self.server.yandexMusicGetPlaylist(name)
	
	def getYandexMusicAlbums(self):#+
		return self.server.yandexMusicGetAlbums()
	
	def getYandexMusicAlbum(self, name):#+
		return self.server.yandexMusicGetAlbum(name)

	def getYandexMusicPlaylistAsync(self, name):#+
		if not self.useInternet:
			return
		r = Request(ReuestEnum.LOAD_YM_PLAYLIST, 
			{'name': name}, 
			self.frames[FRAME_PLAYLISTS].setCurrentPlaylistCb)
		self.addRequest(r)

	def getYandexMusicTrack(self, id):#+
		return self.server.yandexMusicGetMusicTrack(id)
	
	def getYandexMusicGetTracks(self, ids):#+
		return self.server.yandexMusicGetTracks(ids)
	
	def getYandexMusicTrackUrl(self, id):#+
		return self.server.yandexMusicGetTrackUrl(id)

	def loadYandexMusicTrack(self, id):#+
		return self.server.yandexMusicDownloadTrack(id)

	def searchYandexMusicTrack(self, query):
		if not self.useInternet:
			return
		r = Request(ReuestEnum.SEARCH_YM_TRACKS, 
			{'query': query}, 
			self.frames[FRAME_SEARCH].ymSearchCb)
		self.addRequest(r)

	def isYandexMusicInit(self) -> bool:#+
		return self.server.yandexMusicIsInit()

	def addRequest(self, r):
		requestsQueue.append(r)

	def asyncHandler(self):
		localserver = Proxy("PYRONAME:kitsune.music.daemon")
		while True:
			if len(requestsQueue) > 0:
				r = requestsQueue[0]
				requestsQueue.pop(0)
				match r.type:
					case ReuestEnum.YM_GET_FAVORITES:
						r.callback(localserver.yandexMusicGetFavorites())
					case ReuestEnum.GET_LYRICS:
						res = localserver.lyricsGetSongLyrics(r.payload["artist"], r.payload["song"], r.payload["ymId"])
						r.callback(res, r.payload["artist"], r.payload["song"])
					case ReuestEnum.GET_ARTISI_BIO:
						res = localserver.lastfmGetArtistBio(r.payload["artist"])
						r.callback(res, r.payload["artist"])
					case ReuestEnum.LOAD_COVER:
						res = localserver.lastfmGetCover(r.payload["artist"], r.payload["album"], r.payload["ymId"])
						r.callback(res, r.payload["artist"], r.payload["album"])
					case ReuestEnum.SEARCH_YM_TRACKS:
						res = localserver.yandexMusicSearchTrack(r.payload["query"])
						r.callback(res, r.payload["query"])
					case ReuestEnum.LOAD_YM_PLAYLIST:
						ympl = None
						name =  r.payload["name"]
						if  name == YANDEX_MUSIC_LIKES:
							ympl = self.presenter.getYandexMusicFavorites()
						else:
							ympl = self.presenter.getYandexMusicPlaylist(name)
						r.callback(res, ympl, name)
			else:
				time.sleep(0.500)

	def openMusicFile(self, path):
		self.server.openMusicFile(path)

	def playerSavePlaylist(self):
		self.server.playerSavePlaylist()