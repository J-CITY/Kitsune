import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.utils.utils import ColorTheme, getAttr, getColor, loadPlaylist, savePlaylist
from gui.utils.widget import CustomFrame, CustomMultiColumnListBox

from tag_controller import Tag, getTagFromPath, Playlist
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import Screen

from gui.dialog import AddMusicDialog
from gui.dialog_download import DownloadDialog
from gui.dialog import AddMusicDialog, ADD_END,ADD_BEGIN,ADD_AFTER,ADD_BEFORE
from gui.dialog_info import InfoDialog
from strings import *
from typing import List, NoReturn
from tag_controller import TrackType

class PlaylistInfo:
	def __init__(self, t, n) -> NoReturn:
		self.type: TrackType = t
		self.name: str = n

class PlaylistsFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(PlaylistsFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Playlists", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))
		self.curPlaylist: Playlist = Playlist()
		self.playlistsInfo: List[PlaylistInfo] = []
		self.addUpBar()
		
		layout = Layout([1,1], fill_frame=True)
		self.add_layout(layout)

		c = config.playlists.color.split(':')
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.playlists.color_choice.split(':')
		self.color_choice = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.playlists.color_not_focus.split(':')
		self.color_not_focus = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		titlePls = config.playlists.title_playlists
		titlePl = config.playlists.title_playlist
		
		
		self.listPls = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_choice],
			[],
			titles=[titlePls],
			name="Playlists", on_change=self._on_change, on_select=self.openPlaylist)
		self.listPls.choiceCh = config.main_playlist.choice_char
		self.listPls.itemCh = config.main_playlist.item_char
		layout.add_widget(self.listPls, 0)

		self.listPl = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_not_focus],
			[],
			titles=[titlePl],
			name="Playlist", on_select=self.addSong)
		self.listPl.choiceCh = config.main_playlist.choice_char
		self.listPl.itemCh = config.main_playlist.item_char
		layout.add_widget(self.listPl, 1)
		
		self.addDownBar()
		self.fix()

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
							("At the end of playlist", ADD_END),
							("At the beginning of playlist", ADD_BEGIN),
							("After current song", ADD_AFTER),
							("Before current song", ADD_BEFORE)
						],
						playlistLists = pls,
						needNewPlaylist = False,
						needListAdd = True,
						needListPlaylists = True,
						needPlayCb = True,
						presenter=self.presenter, win=name))
			if event.key_code in [ord('l')]:
				if not self.presenter.config.useInternet:
					return
				playlistName = self.listPls._options[self.listPls._line][0][0]
				e = self.curPlaylist.tracks[self.listPl._line]
				url = ""
				name = ""
				if playlistName == "SC:favorites":
					url = self.presenter.scGetStream(e.stream_url).location
					name = e.title
				else:
					url = self.presenter.scGetStream(e["stream_url"]).location
					name = e["title"]
				name = name.replace("\"", "")
				if len(playlistName) > 3 and playlistName[:3] == "SC:" and \
					self.listPl._has_focus and name != "" and url != "":
					fpath = self.presenter.config.download_folder + "/" + name + ".mp3"
					self.presenter.scDownloadName(url, fpath, name)
					self.presenter.dbInsertByPath(fpath)
					self.presenter.medialibUpdate()
					tag = getTagFromPath(fpath)
					self.presenter.mainPlaylistAddSong(ADD_END, False, "current", tag)
			if event.key_code in [ord('L')]:
				if not self.presenter.config.useInternet:
					return
				playlistName = self.listPls._options[self.listPls._line][0][0]

				e = self.curPlaylist.tracks[self.listPl._line]
				url = ""
				name = ""
				if playlistName == "SC:favorites":
					url = self.presenter.scGetStream(e.stream_url).location
					name = e.title
				else:
					url = self.presenter.scGetStream(e["stream_url"]).location
					name = e["title"]
				name = name.replace("\"", "")
				if len(playlistName) > 3 and playlistName[:3] == "SC:" and \
					self.listPl._has_focus and name != "" and url != "":
					self._scene.add_effect(
						DownloadDialog(self._screen, 
							"Download song", url, name,
							["OK", "Cancel"],
							presenter=self.presenter, win="download_sc"))
			if event.key_code in [ord('d')]:
				if self.listPls._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if playlistName[:3] != "SC:":
						rmpl = self.presenter.getPathOfPlaylist(playlistName)
						if os.path.exists(rmpl):
							os.remove(rmpl)
						self.updatePlaylists()
				elif self.listPl._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if playlistName[:3] != "SC:":
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
					if playlistName[:3] != "SC:":
						_from = self.listPl._line
						_to = self.listPl._line-1 if self.listPl._line > 0 else self.listPl._line

						e = self.curPlaylist.tracks[_from]
						self.curPlaylist.tracks[_from] = self.curPlaylist.tracks[_to]
						self.curPlaylist[_to] = e

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
			if event.key_code in [ord('k')]:#swap
				if self.listPl._has_focus:
					playlistName = self.listPls._options[self.listPls._line][0][0]
					if playlistName[:3] != "SC:":
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
			self.presenter.mainPlaylistAddSong(ADD_END, False, "current", e)
	
	def openPlaylist(self):
		self.presenter.mainPlaylistOpen(self.curPlaylist)

	def addSong(self, play=True):
		e = self.curPlaylist.tracks[self.listPl._line]
		if e.type == TrackType.SOUND_CLOUD and not self.presenter.isSoundCloudInit():
			return
		if e.type == TrackType.YANDEX_MUSIC and not self.presenter.isYandexMusicInit():
			return
		if play:
			self.presenter.player.stop()
		self.presenter.mainPlaylistAddSong(ADD_END, play, "current", e)
	
	def updatePlaylists(self):
		self.playlistsInfo = []
		#get local playlists
		tableOptions = []
		localPlaylists = self.presenter.getListOfPlaylists()
		#print(pls)
		if localPlaylists != []:
			for i, e in enumerate(localPlaylists):
				tableOptions.append(([e], i))
				self.playlistsInfo.append(PlaylistInfo(TrackType.LOCAL, e))

		if not self.presenter.config.useInternet:
			return
		
		if self.presenter.isSoundCloudInit():
			scList = ["SoundCloud: likes"]
			scpls = self.presenter.scGetPlaylists()
			for p in scpls:
				scList += [p.title]

			for i, e in enumerate(scList):
				tableOptions.append(([e], len(tableOptions)))
				self.playlistsInfo.append(PlaylistInfo(TrackType.SOUND_CLOUD, e))

		if self.presenter.isYandexMusicInit():
			ymList = ["Yandex Music: likes"]
			ympls = self.presenter.getYandexMusicPlaylists()
			for p in ympls:
				ymList += [p.title]

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
		if currentPlaylist.type == TrackType.YANDEX_MUSIC:
			_curPlaylist = []

			if currentPlaylist.name == "Yandex Music: likes":
				ympl = self.presenter.getYandexMusicFavorites()

				tracksId= []
				for e in ympl:
					tracksId.append(e.id)
				tracks = self.presenter.getYandexMusicGetTracks(tracksId)
				
				self.curPlaylist = Playlist()
				self.curPlaylist.name = "Yandex Music: likes"
				for i, track in enumerate(tracks):
					_curPlaylist.append((["-" + track.title], i))
					t = Tag()
					t.type = TrackType.YANDEX_MUSIC
					t.url = str(track.title)
					t.album = '' if len(track.albums) == 0 else track.albums[0].title
					t.artist = '' if len(track.artists) == 0 else track.artists[0].name
					t.song = track.title
					t.globalId = track.id
					self.curPlaylist.tracks.append(t)
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
			else:
				ympl = self.presenter.getYandexMusicPlaylist(currentPlaylist.name)

				tracksId= []
				for e in ympl:
					tracksId.append(e.id)
				tracks = self.presenter.getYandexMusicGetTracks(tracksId)

				self.curPlaylist = Playlist()
				self.curPlaylist.name = currentPlaylist.name
				for i, track in enumerate(tracks):
					_curPlaylist.append((["-" + track.title], i))
					t = Tag()
					t.type = TrackType.YANDEX_MUSIC
					t.url = str(track.title)
					t.album = '' if len(track.albums) == 0 else track.albums[0].title
					t.artist = track.artists[0].name
					t.song = track.title
					t.globalId = track.id
					self.curPlaylist.tracks.append(t)
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
			return

		if currentPlaylist.type == TrackType.SOUND_CLOUD:
			_curPlaylist = []
			if currentPlaylist.name == "SoundCloud: likes":
				scpl = self.presenter.scGetFavorites()
				self.curPlaylist = Playlist()
				self.curPlaylist.name = "SoundCloud: likes"
				for i, e in enumerate(scpl):
					_curPlaylist.append((["-"+e.title], i))
					t = Tag()
					t.type = TrackType.SOUND_CLOUD
					t.url = str(e.title)
					t.album = ''
					t.artist = ''
					t.song = e.title
					t.globalId = e.id
					self.curPlaylist.tracks.append(t)
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
				return
			else:
				scpls = self.presenter.scGetPlaylists()
				#print(scpls)
				scid = 0
				for p in scpls:
					if p.title == currentPlaylist.name:
						scid = p.ud
						break
				scpl = self.presenter.scGetPlaylistsById(scid)
				self.curPlaylist = Playlist()
				self.curPlaylist.name = currentPlaylist.name
				for i, e in enumerate(scpl):
					_curPlaylist.append((["-"+e.title], i))
					t = Tag()
					t.type = TrackType.SOUND_CLOUD
					t.url = str(e.title)
					t.album = ''
					t.artist = ''
					t.song = e.title
					t.globalId = e.id
					self.curPlaylist.tracks.append(t)
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
			return
		
		path = self.presenter.config.playlist_folder + "/"+ \
			currentPlaylist.name if self.presenter.config.playlist_folder[len(self.presenter.config.playlist_folder)-1] != "/" else currentPlaylist.name
		self.curPlaylist = loadPlaylist(path)
		_curPlaylist = []
		for i, e in enumerate(self.curPlaylist.tracks):
			_curPlaylist.append(([e.artist+" - "+e.song], i))
		self.listPl._options = _curPlaylist
		self.listPl.value = 0

	def setPresenter(self, p):
		self.presenter = p
		self.updatePlaylists()

	def _on_change(self):
		currentPlaylist = self.playlistsInfo[self.listPls.value]
		self.setCurrentPlaylist(currentPlaylist)