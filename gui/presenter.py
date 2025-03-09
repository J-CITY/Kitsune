import threading, time, os
from Pyro5.api import expose, callback, Daemon, Proxy
from Pyro5.api import register_dict_to_class, register_class_to_dict
from core.tag_controller import Tag, Playlist, getTagFromPath, setTagForPath
from core.utils import MusicAddPolitics
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from core.db import *
from gui.utils.widget import CustomFrame
import threading, asyncio
from enum import Enum
from typing import NoReturn, Dict, Optional
from core.tag_controller import playlist_class_to_dict, playlist_dict_to_class
from core.strings import *

PLAYLIST_CURRENT = 'current'

NEED_UPDATE_SONG_TAG = False

class CallbackHandler(object):
	def __init__(self):
		self.presenter = None

	@expose
	@callback
	def default(self):
		pass

	@expose
	@callback
	def updatePlayerItemCb(self, id, tag):
		global NEED_UPDATE_SONG_TAG
		NEED_UPDATE_SONG_TAG = True
		print("data")
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table.playId = id
		print(LogLevel.INFO, "updatePlayerItemCb2")
		self.presenter.song = tag
		print(LogLevel.INFO, "updatePlayerItemCb3")


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

		#TODO get from daemon config
		self.isUseInternet = False
		self.playlistsFolder = "playlists"

	def getUseInternet(self):
		return self.isUseInternet

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

	def getYandexMusicFavorites(self):
		return self.yandexMusicClient.getFavorite()

	def getYandexMusicPlaylists(self):
		return self.yandexMusicClient.getPlaylists()
	
	def getYandexMusicPlaylist(self, name):
		return self.yandexMusicClient.getPlaylist(name)

	def getYandexMusicTrack(self, id):
		return self.yandexMusicClient.getTrack(id)
	
	def getYandexMusicGetTracks(self, ids):
		return self.yandexMusicClient.getTracks(ids)
	
	def getYandexMusicTrackUrl(self, id):
		return self.yandexMusicClient.getTrackUrl(id)

	def lyricsGetSongLyrics(self, artist, song):
		if artist == "" or song == "":
			return ""
		if not self.config.useInternet:
			return ""
		return self.lyricsWiki.getLyrics(artist, song)

	def isYandexMusicInit(self) -> bool:
		return self.yandexMusicClient.isInitial()

	def lastfmGetArtistBio(self, name):
		if not self.config.useInternet:
			return ""
		return self.lastfm.getArtistBio(name)

	def lastfmGetCurArtistBio(self):
		tag = self.player.getTag()
		if tag.artist == "":
			return ""
		else:
			if not self.config.useInternet:
				return ""
			return self.lastfm.getArtistBio(tag.artist)

	def lastfmSaveAlbum(self, artist, album):
		return self.lastfm.saveAlbumArt(artist, album)

	def lastfmGetAlbumUrl(self, artist, album):
		return self.lastfm.getAlbumImageUrl(artist, album)

	def dbSelect(self, e):
		return self.db.select(e)

	def dbSearch(self, text):
		return self.db.search(text)

	def dbExecute(self, text, params):
		return self.db.execute(text, params)

	def dbInsertByPath(self, path):
		self.db.insertByPath(path)

	def playerGetCurTag(self):#+
		return self.server.playerGetCurrentTag()

	def playerPlayById(self, id):#+
		self.song = self.server.playerPlayById(id)

	def playerPlay(self, song):#+
		tag = getTagFromPath(song)
		tag.length = self.server.playerGetSongLength()
		self.song = tag
		#self.player.playlist.tracks = [tag]
		self.server.playerSetCurrentPlaylist([tag])
		self.server.play()

	def playerStop(self):#+
		self.server.stop()

	def playerSwap(self, _from, _to):#+
		if _from == _to:
			return
		self.server.playerSwap(_from, _to)
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table.updateList(self.server.playerGetPlaylist().tracks)

	def playerDelete(self, id):#+
		self.server.playerDelete(id)
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table.updateList(self.server.playerGetPlaylist().tracks)
	
	def playlistAddPlaylist(self, pos, isPlay, name):
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

	def playlistAddSong(self, pos, isPlay, name):
		e = self.frames[FRAME_PLAYLISTS].curPlaylist.tracks[self.frames[FRAME_PLAYLISTS].listPl._line]
		self.mainPlaylistAddSong(pos, isPlay, name, e)

	def mainPlaylistUpdateList(self):#+
		self.frames[FRAME_MAIN_PLAYLIST].table.updateList(self.server.playerGetPlaylist().tracks)
	
	def mainPlaylistOpen(self, pl):#+
		for i, p in enumerate(pl):
			p.id = i
		self.player.playlist = pl
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table.updateList(pl)
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table.value = 0
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table._line = 0

	def medialibCreateNewPlaylistAndSaveSong(self, playlistName):
		path = self.config.playlist_folder + "/"+ \
			playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
		
		song = self.medialibGetCurrentTag()
		song.id = 0
		savePlaylist([song], path)
		self.playlistsUpdatePlaylists()

	def medialibAddSong(self, pos, isPlay, name):
		e = self.medialibGetCurrentTag()
		self.mainPlaylistAddSong(pos, isPlay, name, e)

	def searchAddSong(self, pos, isPlay, name):
		e = self.search.getCurTag()
		if e != None:
			self.mainPlaylistAddSong(pos, isPlay, name, e)

	def medialibGetCurrentTag(self):#+
		return self.frames[FRAME_MEDIALIB].getCurrentTag()

	#TODO: create tag in browser
	def mainPlaylistAddSong(self, addParam, needPlay: bool, playlistName: str, _tag=None):#+
		if _tag == None:
			song = self.frames[FRAME_BROWSER].browser.value
			tag = getTagFromPath(song)
		else:
			tag = _tag

		if len(self.presenter.frames[FRAME_MAIN_PLAYLIST].table._options) > 0 and self.presenter.frames[FRAME_MAIN_PLAYLIST].table._line < 0:
			self.presenter.frames[FRAME_MAIN_PLAYLIST].table._line = 0

		if playlistName == PLAYLIST_CURRENT:
			playlist = self.server.playerGetPlaylist()
		else:
			path = os.path.join(self.playlistsFolder, playlistName)
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
			tag.id = self.presenter.frames[FRAME_MAIN_PLAYLIST].getCurrentLineId()+1 if playlistName == PLAYLIST_CURRENT else 0
			if tag.id == len(playlist.tracks):
				playlist.tracks = playlist.tracks[0:tag.id]+[tag]
			else:
				playlist.tracks = playlist.tracks[0:tag.id]+[tag]+playlist.tracks[tag.id:]
			for e in playlist.tracks[tag.id+1:]:
				e.id+=1
		elif addParam == MusicAddPolitics.ADD_BEFORE:
			tag.id = self.presenter.frames[FRAME_MAIN_PLAYLIST].getCurrentLineId() if playlistName == PLAYLIST_CURRENT else 0
			if tag.id == 0:
				playlist.tracks = [tag]+playlist.tracks[tag.id:]
			else:
				playlist.tracks = playlist.tracks[0:tag.id]+ [tag]+playlist.tracks[tag.id:]
			for e in playlist.tracks[tag.id+1:]:
				e.id+=1

		if playlistName == PLAYLIST_CURRENT:
			self.server.playerSetCurrentPlaylist(playlist.tracks)
			self.song = tag
			self.presenter.frames[FRAME_MAIN_PLAYLIST].table.updateList(playlist.tracks)
			if needPlay:
				self.mainPlaylistSetPlayId(tag.id)
				self.player.play()
		else:
			savePlaylist(playlist.tracks, path)
			self.playlistsUpdatePlaylists()

	def browserCreateNewPlaylistAndSaveSong(self, playlistName):#+
		frame = self.presenter.frames.get(FRAME_BROWSER, None)
		if frame is None:
			log(LogLevel.INFO, "browserCreateNewPlaylistAndSaveSong: 'BrowserFrame' doesn`t exist")
			return

		pathPlaylist = os.path.join(self.playlistsFolder, playlistName)
		song = self.frames[FRAME_BROWSER].browser.value
		tag = getTagFromPath(song)
		tag.length = self.player.getLen()
		tag.id = 0
		savePlaylist([tag], pathPlaylist)
		self.playlistsUpdatePlaylists()

	# TODO: think this is should delete
	def mainPlaylistSetPlayId(self, id):#+
		self.presenter.frames[FRAME_MAIN_PLAYLIST].table.playId = id
		self.server.playerSetPlaylistId(id)

	def barUpdate(self):#+
		localserver = Proxy("PYRONAME:kitsune.music.daemon")
		while True:
			tag = localserver.playerGetCurrentTagWithLength()
			self.frames[FRAME_MAIN_PLAYLIST].table.playId = tag.id
			self.song = tag
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

				if localserver.playerGetIsPlay():
					tag['length'] = int(localserver.playerGetSongLength())
					tag['curLength'] = int(localserver.playerGetCurrentSongProgress())
					self.upBar.update(tag)
					self.downBar.update(tag)
			time.sleep(.200)

	def run(self):#+
		thread = threading.Thread(target=self.barUpdate)
		thread.daemon = True
		thread.start()

	def setFrameToBars(self, fstr):
		frame = self.presenter.frames.get(fstr, None)
		if frame is None:
			return
		self.upBar.setFrame(frame)
		self.downBar.setFrame(frame)

	def createNewPlaylistAndSaveMainPlaylist(self, playlistName):
		path = self.config.playlist_folder + "/"+ \
			playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
		savePlaylist(self.player.playlist, path)
		self.playlistsUpdatePlaylists()

	def createNewPlaylistFromSearch(self, playlistName):
		path = os.path.join(self.playlistsFolder, playlistName)
		e = self.search.getCurTag()
		if e == None:
			return
		savePlaylist([e], path)
		self.playlistsUpdatePlaylists()

	def medialibCreateNewPlaylistAlbum(self, playlistName):
		path = os.path.join(self.playlistsFolder, playlistName)
		playlist = self.medialibGetCurrentAlbum()
		savePlaylist(playlist, path)
		self.playlistsUpdatePlaylists()

	def medialibGetCurrentAlbum(self):#+
		return self.frames[FRAME_MEDIALIB].getCurrentAlbum()

	def getListOfPlaylists(self) -> List[str]:#+
		return self.server.getListOfPlaylists()

	def getPathOfPlaylist(self, name):#+
		return os.path.join(self.playlistsFolder, name)

	def playlistsUpdatePlaylists(self):
		self.frames[FRAME_PLAYLISTS].updatePlaylists()

	#TODO: del, not used
	def mainPlaylistUpdatePlayItem(self):#+
		self.mainPlaylistSetPlayId(self.player.playlistId)
		tag = self.player.playlist.tracks[self.player.playlistId]
		tag.length = self.player.getLen()
		self.song = tag

	def playerEventControl(self, event):
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
				#TODO set num from config
				self.server.move(5)
			if event.key_code in [ord(',')]:
				self.server.move(-5)
			if event.key_code in [ord('-')]:
				self.server.volumeDown()
			if event.key_code in [ord('=')]:
				self.server.volumeUp()
			if event.key_code in [ord('v')]:
				self.server.mute()
			if event.key_code in [ord('b')]:
				#TODO: set modes from config
				self.server.changeMode()
			if event.key_code in [ord('c')]:
				self.server.changeCrossfade()

	def eqSetLevelParam(self, param):
		self.player.setEqLevelParam(param)
		self.player.setEqParams()

	def eqSetSpeedParam(self ,param):
		self.player.setEqSpeedParam(param)
		self.player.setEqParams()

	def eqSetBassParam(self, param):
		self.player.setEqBass(param)
		self.player.setEqParams()
	def eqSetEchoParam(self, param):
		self.player.setEqEcho(param)
		self.player.setEqParams()

	def eqSetChorusParam(self, param):
		self.player.setEqChorus(param)
		self.player.setEqParams()

	def eqSetFlangeParam(self, param):
		self.player.setEqFlange(param)
		self.player.setEqParams()
	def eqSetReverbParam(self, param):
		self.player.setEqReverb(param)
		self.player.setEqParams()

	def playerGetWaveData(self, isSterio, col):
		return self.player.getWaveData(isSterio, col)
	def playerGetFFTData(self, isSterio, col):
		return self.player.getFFTData(isSterio, col)

	def barGetFrameName(self):
		return self.upBar.getFrameName()

	def artistinfoUpdateText(self):
		if not self.config.useInternet:
			return ''
		self.artistinfo.updateText()

	def lyricsUpdateText(self):
		if not self.config.useInternet:
			return
		self.lyrics.updateText()

	def playerGetLen(self):#+
		return self.server.playerGetSongLength()

	def playerGetBuf(self):#+
		return self.server.playerGetCurrentSongProgress()
