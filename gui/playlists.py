import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from core.utils import ColorTheme, getAttr, getColor, MusicAddPolitics
from gui.utils.widget import CustomFrame, CustomMultiColumnListBox

from core.tag_controller import Tag, getTagFromPath, Playlist, TrackType, loadPlaylist, savePlaylist
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import Screen

from gui.dialog import AddMusicDialog
from gui.dialog_download import DownloadDialog
from gui.dialog import AddMusicDialog
from gui.dialog_info import InfoDialog
from core.strings import *
from typing import List, NoReturn

class PlaylistInfo:
	def __init__(self, t, n) -> NoReturn:
		self.type: TrackType = t
		self.name: str = n

class PlaylistsFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(PlaylistsFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name=FRAME_PLAYLISTS, upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))
		self.curPlaylist: Playlist = Playlist()
		self.playlistsInfo: List[PlaylistInfo] = []
		self.addUpBar()
		
		layout = Layout([1,1], fill_frame=True)
		self.add_layout(layout)

		c = presenter.config.playlists.color.split(':')
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = presenter.config.playlists.color_choice.split(':')
		self.color_choice = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = presenter.config.playlists.color_not_focus.split(':')
		self.color_not_focus = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		titlePls = presenter.config.playlists.title_playlists
		titlePl = presenter.config.playlists.title_playlist
		
		self.listPls = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_choice],
			[],
			titles=[titlePls],
			name=FRAME_PLAYLISTS, on_change=self._on_change, on_select=self.openPlaylist)
		self.listPls.choiceCh = presenter.config.main_playlist.choice_char
		self.listPls.itemCh = presenter.config.main_playlist.item_char
		layout.add_widget(self.listPls, 0)

		self.listPl = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_not_focus],
			[],
			titles=[titlePl],
			name="Playlist", on_select=self.addSong)
		self.listPl.choiceCh = presenter.config.main_playlist.choice_char
		self.listPl.itemCh = presenter.config.main_playlist.item_char
		layout.add_widget(self.listPl, 1)

		self.shortPlaylistCache = {}
		self.fullPlaylistCache = {}

		self.addDownBar()
		self.fix()
		self.setPresenter(presenter)

	def popup(self):
		pass

	def details(self):
		pass

	def process_event(self, event):
		# Do the key handling for this Frame.
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)
			if event.key_code in [ord('e')]:
				if self.listPls._has_focus:
					self.addPlaylist()
				else:
					self.addSong(False)
			if event.key_code in [ord('E')]:
				name = ""
				title = ""
				if self.listPls._has_focus:
					name = "Playlists"
					title = "Add playlist"
				elif self.listPl._has_focus:
					name = "Playlist"
					title = "Add song"
				pls = self.presenter.getListOfPlaylists()
				for i, e in enumerate(pls):
					pls[i] = (e, i+1)
				pls = [(CURRENT_PLAYLIST, 0)] + pls
				self._scene.add_effect(
					AddMusicDialog(self._screen, 
						title, 
						["OK", "Cancel"], 
						addList = [
							("At the end of playlist", MusicAddPolitics.ADD_END),
							("At the beginning of playlist", MusicAddPolitics.ADD_BEGIN),
							("After current song", MusicAddPolitics.ADD_AFTER),
							("Before current song", MusicAddPolitics.ADD_BEFORE)
						],
						playlistLists = pls,
						needNewPlaylist = False,
						needListAdd = True,
						needListPlaylists = True,
						needPlayCb = True,
						presenter=self.presenter, win=name))
			if event.key_code in [ord('l')]:
				if not self.presenter.getUseInternet():
					return
				if self.currentPlaylist.type == TrackType.YANDEX_MUSIC and self.curPlaylist.getSize() > 0:
					e = self.curPlaylist.tracks[self.listPl._line]
					self.presenter.loadYandexMusicTrack(e.globalId)
			
			# Delete playlist or playlist item
			if event.key_code in [ord('d')]:
				if self.listPls._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if self.currentPlaylist.type == TrackType.LOCAL:
						rmpl = self.presenter.getPathOfPlaylist(playlistName)
						if os.path.exists(rmpl):
							os.remove(rmpl)
						self.updatePlaylists()
				elif self.listPl._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if self.currentPlaylist.type == TrackType.LOCAL:
						self.curPlaylist.tracks = self.curPlaylist.tracks[:self.listPl._line] + self.curPlaylist.tracks[self.listPl._line+1:]
						_curPlaylist = []
						for i, e in enumerate(self.curPlaylist.tracks):
							_curPlaylist.append(([e.artist+" - "+e.song], i))
						self.listPl._options = _curPlaylist
						self.listPl.value = 0
						self.listPl._line = 0
						path = self.presenter.getPathOfPlaylist(playlistName)
						savePlaylist(self.curPlaylist, path)
			if event.key_code in [ord('j')]:#swap
				if self.listPl._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if self.currentPlaylist.type == TrackType.LOCAL:
						_from = self.listPl._line
						_to = self.listPl._line-1 if self.listPl._line > 0 else self.listPl._line
						#TODO: move in to func
						e = self.curPlaylist.tracks[_from]
						self.curPlaylist.tracks[_from] = self.curPlaylist.tracks[_to]
						self.curPlaylist.tracks[_to] = e

						e = self.curPlaylist.tracks[_from].id
						self.curPlaylist.tracks[_from].id = self.curPlaylist.tracks[_to].id
						self.curPlaylist.tracks[_to].id = e

						_curPlaylist = []
						for i, e in enumerate(self.curPlaylist.tracks):
							_curPlaylist.append(([e.artist+" - "+e.song], i))
						self.listPl._options = _curPlaylist

						self.listPl._line = _to
						self.listPl.value = self.listPl._options[self.listPl._line][1]
						path = self.presenter.getPathOfPlaylist(playlistName)
						savePlaylist(self.curPlaylist, path)
						#TODO: move in to func end
			if event.key_code in [ord('k')]:#swap
				if self.listPl._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if self.currentPlaylist.type == TrackType.LOCAL:
						_from = self.listPl._line
						_to = self.listPl._line+1 if self.listPl._line < len(self.listPl._options)-1 else self.listPl._line
				
						e = self.curPlaylist.tracks[_from]
						self.curPlaylist.tracks[_from] = self.curPlaylist.tracks[_to]
						self.curPlaylist.tracks[_to] = e

						e = self.curPlaylist.tracks[_from].id
						self.curPlaylist.tracks[_from].id = self.curPlaylist.tracks[_to].id
						self.curPlaylist.tracks[_to].id = e
						
						_curPlaylist = []
						for i, e in enumerate(self.curPlaylist.tracks):
							_curPlaylist.append(([e.artist+" - "+e.song], i))
						self.listPl._options = _curPlaylist

						self.listPl._line = _to
						self.listPl.value = self.listPl._options[self.listPl._line][1]
						path = self.presenter.getPathOfPlaylist(playlistName)
						savePlaylist(self.curPlaylist, path)
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

		super(PlaylistsFrame, self).process_event(event)
		
		if self.listPls._has_focus:
			self.listPls._chColors = [self.color_choice]
		else:
			self.listPls._chColors = [self.color_not_focus]
		if self.listPl._has_focus:
			self.listPl._chColors = [self.color_choice]
		else:
			self.listPl._chColors = [self.color_not_focus]
		return

	def addPlaylist(self):
		for e in self.curPlaylist.tracks:
			self.presenter.mainPlaylistAddSong(MusicAddPolitics.ADD_END, False, CURRENT_PLAYLIST, e)
	
	def openPlaylist(self):
		self.presenter.mainPlaylistOpen(self.curPlaylist)

	def addSong(self, play=True):
		e = self.curPlaylist.tracks[self.listPl._line]
		if e.type == TrackType.YANDEX_MUSIC and not self.presenter.isYandexMusicInit():
			return
		if play:
			self.presenter.playerStop()
		self.presenter.mainPlaylistAddSong(MusicAddPolitics.ADD_END, play, CURRENT_PLAYLIST, e)
	
	def updatePlaylists(self):
		self.playlistsInfo = []
		# Get local playlists
		tableOptions = []
		localPlaylists = self.presenter.getListOfPlaylists()
		if localPlaylists != []:
			for i, e in enumerate(localPlaylists):
				tableOptions.append(([e], i))
				self.playlistsInfo.append(PlaylistInfo(TrackType.LOCAL, e))

		if not self.presenter.getUseInternet():
			return
		#Get playlists from YM
		if self.presenter.isYandexMusicInit():
			ymList = [YANDEX_MUSIC_LIKES]
			ympls = self.presenter.getYandexMusicPlaylists()
			for p in ympls:
				ymList += [p["title"]]
				if len(p['tracks']) > 0:
					self.shortPlaylistCache[p["title"]] = p

			for i, e in enumerate(ymList):
				tableOptions.append(([e], len(tableOptions)))
				self.playlistsInfo.append(PlaylistInfo(TrackType.YANDEX_MUSIC, e))

		self.listPls._options = tableOptions
		self.listPls.value = 0

		if self.playlistsInfo == []:
			return
		currentPlaylist = self.playlistsInfo[0]
		self.setCurrentPlaylist(currentPlaylist)

	def setCurrentPlaylist(self, currentPlaylist: PlaylistInfo) -> NoReturn:
		# For YM playlist
		if currentPlaylist.type == TrackType.YANDEX_MUSIC:
			_curPlaylist = []
			
			# Get tracks ids
			ympl = None
			if currentPlaylist.name in self.shortPlaylistCache:
				ympl = self.shortPlaylistCache[currentPlaylist.name]
			else:
				if currentPlaylist.name == YANDEX_MUSIC_LIKES:
					ympl = self.presenter.getYandexMusicFavorites()
				else:
					ympl = self.presenter.getYandexMusicPlaylist(currentPlaylist.name)
				self.shortPlaylistCache[currentPlaylist.name] = ympl

			# Get tracks
			if currentPlaylist.name in self.fullPlaylistCache:
				tracks = self.fullPlaylistCache[currentPlaylist.name]
			else:
				tracksId= []
				for trackId in ympl['tracks']:
					tracksId.append(trackId)
				tracks = self.presenter.getYandexMusicGetTracks(tracksId)
				self.fullPlaylistCache[currentPlaylist.name] = tracks

			self.curPlaylist = Playlist()
			self.curPlaylist.name = currentPlaylist.name
			for i, track in enumerate(tracks):
				_curPlaylist.append((["-" + track['title']], i))
				t = Tag()
				t.type = TrackType.YANDEX_MUSIC
				t.url = ''
				for i, a in enumerate(track['albums']):
					if i != 0:
						t.album += ","
					t.album += a
				for i, a in enumerate(track['artists']):
					if i != 0:
						t.artist += ","
					t.artist += a
				t.song = track['title']
				t.globalId = track['id']
				t.ymHasLyrics = track['lyrics_available']
				t.ymCoverUrl = track['cover_uri']
				self.curPlaylist.tracks.append(t)
			self.listPl._options = _curPlaylist
			self.listPl.value = 0
			return

		# For local playlist
		path = os.path.join(self.presenter.getPlaylistFolder(), currentPlaylist.name)
		self.curPlaylist = loadPlaylist(path)
		_curPlaylist = []
		for i, e in enumerate(self.curPlaylist.tracks):
			_curPlaylist.append(([e.artist+" - "+e.song], i))
		self.listPl._options = _curPlaylist
		self.listPl.value = 0

	def setPresenter(self, p):
		self.presenter = p
		self.presenter.addFrame(self.frameName, self)
		self.updatePlaylists()

	def _on_change(self):
		self.currentPlaylist = self.playlistsInfo[self.listPls.value]
		self.setCurrentPlaylist(self.currentPlaylist)
		