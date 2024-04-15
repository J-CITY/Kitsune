import threading, time, os
from tag_controller import Tag, Playlist, getTagFromPath, setTagForPath
from gui.utils.utils import savePlaylist, loadPlaylist
from gui.utils.utils import ADD_END, ADD_BEGIN, ADD_AFTER, ADD_BEFORE
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from db import *

from gui.utils.utils import createNotify
from gui.utils.widget import CustomFrame

import threading
from enum import Enum
from typing import NoReturn, Dict, Optional

PLAYLIST_CURRENT = 'current'

class EFrame(Enum):
    MAIN_PLAYLIST = 1

class Presenter:
	def __init__(self, config):
		self.config = config
		self.frames = {}

		self.song = None

		self.playlistsCash: Dict[str, Playlist] = {}
	
	def tryGetPlaylist(self, name: str) -> Optional[Playlist]:
		if name in self.playlistsCash:
			return self.playlistsCash[name]
		return None

	def worker(self, artist: str, album: str, song: str) -> NoReturn:
		res = self.lastfmSaveAlbum(artist, album)
		path = self.config.cash_folder + ("/album.png" if res else "/defAlbum.png")
		createNotify(artist, album + " - " + song, path, self.config.notify_wait)

	def createNotify(self, title: str="", msg: str="", ico: str="") -> NoReturn:
		createNotify(title, msg, ico, self.config.notify_wait)

	def createNotifySong(self, artist: str="", album: str="",  song: str=""):
		if artist=="" or album=="" or  song=="":
			createNotify(artist, album + " - " + song, self.config.cash_folder + "/defAlbum.png", self.config.notify_wait)
			return
		t = threading.Thread(target=self.worker, args=(artist, album, song, ))
		t.start()

	def setPlayer(self, player) -> NoReturn:
		self.player = player

	def addFrame(self, id: EFrame, frame: CustomFrame) -> NoReturn:
		self.frames[id] = frame
		
	def setMainPlaylist(self, w):
		self.mainplaylist = w
	def setPlaylists(self, w):
		self.playlists = w
	def setBrowser(self, w):
		self.browser = w
	def setClock(self, w):
		self.clock = w
	def setEqualizer(self, w):
		self.equalizer = w
	def setUpBar(self, w):
		self.upBar = w
	def setDownBar(self, w):
		self.downBar = w
	def setSoundCloud(self, w):
		self.soundCloud = w
	def setLastfm(self, w):
		self.lastfm = w
	def setVisualization(self, w):
		self.visualization = w
	def setDb(self, w):
		self.db = w
	def setMedialib(self, w):
		self.medialib = w
	def setArtistInfo(self, w):
		self.artistinfo = w
	def setLyrics(self, w):
		self.lyrics = w
	def setLyricsWiki(self, w):
		self.lyricsWiki = w
	def setSearch(self, w):
		self.search = w
	def setYandexMusicClient(self, c):
		self.yandexMusicClient = c

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

	def isSoundCloudInit(self) -> bool:
		return self.soundCloud.isInitial()
	
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

	def scSearch(self, text):
		if not self.config.useInternet:
			return
		return self.soundCloud.search(text)

	def scLike(self, id):
		if not self.config.useInternet:
			return
		self.soundCloud.like(id)

	def dbExecute(self, text, params):
		return self.db.execute(text, params)

	def dbInsertByPath(self, path):
		self.db.insertByPath(path)

	def playerGetCurTag(self):
		return self.player.getTag()

	def playerPlayById(self, id):
		if len(self.player.playlist.tracks) > id:
			tag = self.player.playlist.tracks[id]
			tag.length = self.player.getLen()
			if tag.globalId != -1 and tag.type != TrackType.YANDEX_MUSIC: #TODO: move to play()
				if not self.config.useInternet:
					return
				s = self.soundCloud.getSongUrlById(tag.globalId)
				tag.url = self.soundCloud.getStreamByUrl(s.stream_url).location
			self.song = tag
			self.player.playlistId = id
			self.player.stop()
			self.player.play()

	def playerPlay(self, song):
		tag = getTagFromPath(song)
		tag.length = self.player.getLen()
		self.song = tag
		self.player.playlist.tracks = [tag]
		self.player.play()
	def playerSwap(self, _from, _to):
		if _from == _to:
			return
		ida = self.player.playlist.tracks[_from].id
		idb = self.player.playlist.tracks[_to].id
		itm = self.player.playlist.tracks[_from]
		self.player.playlist.tracks[_from] = self.player.playlist.tracks[_to]
		self.player.playlist.tracks[_to] = itm
		self.player.playlist.tracks[_from].id = ida
		self.player.playlist.tracks[_to].id = idb
		self.mainplaylist.table.updateList(self.player.playlist.tracks)

	def playerDelete(self, id):
		self.player.playlist.tracks = self.player.playlist.tracks[0:id]+self.player.playlist.tracks[id+1:]
		for i in self.player.playlist.tracks[id:]:
			i.id-=1
		self.mainplaylist.table.updateList(self.player.playlist.tracks)
	
	def playlistAddPlaylist(self, pos, isPlay, name):
		spl = self.playlists.curPlaylist
		#if name == "current" and (pos == ADD_BEFORE or pos == ADD_AFTER):
		#	pos = ADD_END
		if pos == ADD_END or pos == ADD_BEFORE:
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
	
	def medialibAddAlbum(self, pos, isPlay, name):
		spl = self.medialibGetCurrentAlbum()
		if pos == ADD_END or pos == ADD_BEFORE:
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

	def medialibUpdate(self):
		self.medialib.updateMl()

	def playlistAddSong(self, pos, isPlay, name):
		e = self.playlists.curPlaylist.tracks[self.playlists.listPl._line]
		self.mainPlaylistAddSong(pos, isPlay, name, e)

	def mainPlaylistUpdateList(self):
		self.mainplaylist.table.updateList(self.player.playlist.tracks)
	
	def mainPlaylistOpen(self, pl):
		for i, p in enumerate(pl):
			p.id = i
		self.player.playlist = pl
		self.mainplaylist.table.updateList(pl)
		self.mainplaylist.table.value = 0
		self.mainplaylist.table._line = 0

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

	def medialibGetCurrentTag(self):
		return self.medialib.getCurrentTag()

	def mainPlaylistAddSong(self, addParam, needPlay: bool, playlistName: str, _tag=None):
		if _tag == None:
			song = self.browser.browser.value
			tag = getTagFromPath(song)
			#tag.length = self.player.getLen()
		else:
			tag = _tag
		
		#if playlistName == "current" and (addParam == ADD_BEFORE or addParam == ADD_AFTER):
		#	addParam = ADD_END

		if len(self.mainplaylist.table._options) > 0 and self.mainplaylist.table._line < 0:
			self.mainplaylist.table._line = 0

		#fun
		if playlistName == PLAYLIST_CURRENT:
			playlist = self.player.playlist
		else:
			path = self.config.playlist_folder + "/"+ \
				playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
			playlist = loadPlaylist(path)

		#Fun
		if addParam == ADD_END:
			tag.id = len(playlist.tracks)
			playlist.tracks.append(tag)
		elif addParam == ADD_BEGIN:
			tag.id = 0
			playlist.tracks = [tag] + playlist.tracks
			for e in playlist.tracks[1:]:
				e.id+=1
		elif addParam == ADD_AFTER:
			tag.id = self.mainplaylist.getCurrentLineId()+1 if playlistName == PLAYLIST_CURRENT else 0
			if tag.id == len(playlist.tracks):
				playlist.tracks = playlist.tracks[0:tag.id]+[tag]
			else:
				playlist.tracks = playlist.tracks[0:tag.id]+[tag]+playlist.tracks[tag.id:]
			for e in playlist.tracks[tag.id+1:]:
				e.id+=1
		elif addParam == ADD_BEFORE:#befor
			tag.id = self.mainplaylist.getCurrentLineId() if playlistName == PLAYLIST_CURRENT else 0
			if tag.id == 0:
				playlist.tracks = [tag]+playlist.tracks[tag.id:]
			else:
				playlist.tracks = playlist.tracks[0:tag.id]+ [tag]+playlist.tracks[tag.id:]
			for e in playlist.tracks[tag.id+1:]:
				e.id+=1
		#fun
		if playlistName == PLAYLIST_CURRENT:
			self.player.playlist.tracks = playlist.tracks
			self.song = tag
			self.mainplaylist.table.updateList(playlist.tracks)
			if needPlay:
				self.mainPlaylistSetPlayId(tag.id)
				self.player.play()
		else:
			savePlaylist(playlist.tracks, path)
			self.playlistsUpdatePlaylists()
		
	def createNewPlaylistAndSaveSong(self, playlistName):
		path = self.config.playlist_folder + "/"+ \
			playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
		
		song = self.browser.browser.value
		tag = getTagFromPath(song)
		tag.length = self.player.getLen()
		tag.id = 0
		savePlaylist([tag], path)
		self.playlistsUpdatePlaylists()

	def mainPlaylistSetPlayId(self, id):
		self.mainplaylist.table.playId = id
		self.player.playlistId = id

	def barUpdate(self):
		while True:
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
					'volume': str(int(self.player.getVolume())),
					'maxVolume': str(100),
					'mode': self.player.mode,
					'crossfade': self.player.crossfade,
				}

				if self.player.getIsPlay():
					tag['length'] = int(self.player.getLen())
					tag['curLength'] = int(self.player.getBuf())
					self.upBar.update(tag)
					self.downBar.update(tag)
			time.sleep(.200)

	def playerUpdate(self):
		self.player.update()

	def run(self):
		thread = threading.Thread(target=self.barUpdate)
		thread.daemon = True
		thread.start()
		threadPlayer = threading.Thread(target=self.playerUpdate)
		threadPlayer.daemon = True
		threadPlayer.start()

	def setFrameToBars(self, fstr):
		if fstr == "Browser":
			frame = self.browser
		if fstr == "MainPlaylist":
			frame = self.mainplaylist
		if fstr == "Playlists":
			frame = self.playlists
		if fstr == "Clock":
			frame = self.clock
		if fstr == "Equalizer":
			frame = self.equalizer
		if fstr == "Visualizer":
			frame = self.visualization
		if fstr == "Medialib":
			frame = self.medialib
		if fstr == "ArtistInfo":
			if not self.config.useInternet:
				return
			frame = self.artistinfo
		if fstr == "Lyrics":
			if not self.config.useInternet:
				return
			frame = self.lyrics
		if fstr == "Search":
			frame = self.search
		self.upBar.setFrame(frame)
		self.downBar.setFrame(frame)

	def createNewPlaylistAndSaveMainPlaylist(self, playlistName):
		path = self.config.playlist_folder + "/"+ \
			playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
		savePlaylist(self.player.playlist, path)
		self.playlistsUpdatePlaylists()

	def createNewPlaylistFromSearch(self, playlistName):
		path = self.config.playlist_folder + "/"+ \
			playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
		
		e = self.search.getCurTag()
		if e == None:
			return
		savePlaylist([e], path)
		self.playlistsUpdatePlaylists()

	def medialibCreateNewPlaylistAlbum(self, playlistName):
		path = self.config.playlist_folder + "/"+ \
			playlistName if self.config.playlist_folder[len(self.config.playlist_folder)-1] != "/" else playlistName
		playlist = self.medialibGetCurrentAlbum()
		savePlaylist(playlist, path)
		self.playlistsUpdatePlaylists()

	def medialibGetCurrentAlbum(self):
		return self.medialib.getCurrentAlbum()

	def getListOfPlaylists(self) -> List[str]:
		arr = os.listdir(self.config.playlist_folder)
		return arr

	def getPathOfPlaylist(self, name):
		return self.config.playlist_folder + "/" + name

	def playlistsUpdatePlaylists(self):
		self.playlists.updatePlaylists()

	def mainPlaylistUpdatePlayItem(self):
		self.mainPlaylistSetPlayId(self.player.playlistId)
		tag = self.player.playlist.tracks[self.player.playlistId]
		tag.length = self.player.getLen()
		self.song = tag

	def playerEventControl(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('p')]:
				self.player.pause()
			if event.key_code in [ord('S')]:
				self.player.stop()
			if event.key_code in [ord('>')]:
				self.player.stop()
				self.player.next()
				self.mainPlaylistUpdatePlayItem()
			if event.key_code in [ord('<')]:
				self.player.stop()
				self.player.prev()
				self.mainPlaylistUpdatePlayItem()
			if event.key_code in [ord('.')]:
				self.player.move(5)
			if event.key_code in [ord(',')]:
				self.player.move(-5)
			if event.key_code in [ord('-')]:
				self.player.setVolume(self.player.volume-0.02)
			if event.key_code in [ord('=')]:
				self.player.setVolume(self.player.volume+0.02)
			if event.key_code in [ord('v')]:
				self.player.offOnVolume()
			if event.key_code in [ord('b')]:
				self.player.mode = (self.player.mode+1) % 5
			if event.key_code in [ord('c')]:
				self.player.crossfade = not self.player.crossfade

	def scGetFavorites(self):
		if not self.config.useInternet:
			return None
		return self.soundCloud.getFavorites()
	def scGetPlaylists(self):
		if not self.config.useInternet:
			return None
		return self.soundCloud.getPlaylists()
	def scGetStream(self, url):
		if not self.config.useInternet:
			return None
		return self.soundCloud.getStreamByUrl(url)
	def scGetPlaylistById(self, id):
		if not self.config.useInternet:
			return None
		return self.soundCloud.getPlaylistById(id)
	def scDownloadName(self, url, path, name):
		if not self.config.useInternet:
			return
		self.soundCloud.downloadName(url, path, name)

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

	def playerGetLen(self):
		return self.player.getLen()
	def playerGetBuf(self):
		return self.player.getBuf()
	
	def saveSongsMetadatas(self, path, tag):
		setTagForPath(path, tag)

	
