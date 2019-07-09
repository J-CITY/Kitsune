import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.utils import ColorTheme, getAttr, getColor, loadPlaylist, savePlaylist
from gui.utils.widget import CustomFrame, CustomMultiColumnListBox

from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from gui.dialog_download import DownloadDialog
from gui.dialog import AddMusicDialog, ADD_END,ADD_BEGIN,ADD_AFTER,ADD_BEFORE
from gui.dialog_info import InfoDialog
from strings import *

class PlaylistsFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(PlaylistsFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Playlists", bg=getColor(config.bg_color))
		self.curPlaylist = []

		self.upBar = upBar
		self.downBar = downBar

		i = 0
		for l in upBar.layouts:
			_l = Layout([l[0],l[1],l[2]])
			self.add_layout(_l)
			_l.add_widget(upBar.lables[i], 0)
			_l.add_widget(upBar.lables[i+1], 1)
			_l.add_widget(upBar.lables[i+2], 2)
			i+=3
		
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
		i = 0
		for l in downBar.layouts:
			_l = Layout([l[0],l[1],l[2]])
			self.add_layout(_l)
			_l.add_widget(downBar.lables[i], 0)
			_l.add_widget(downBar.lables[i+1], 1)
			_l.add_widget(downBar.lables[i+2], 2)
			i+=3
		
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
				if self.isSCPlaylist:
					if self.listPls._has_focus:
						#self.addPlaylist()
						pass
					else:
						self.addSCSong(False)
				else:
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
				e = self.curPlaylist[self.listPl._line]
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

				e = self.curPlaylist[self.listPl._line]
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
						self.curPlaylist = self.curPlaylist[:self.listPl._line] + self.curPlaylist[self.listPl._line+1:]
						_curPlaylist = []
						for i, e in enumerate(self.curPlaylist):
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

						e = self.curPlaylist[_from]
						self.curPlaylist[_from] = self.curPlaylist[_to]
						self.curPlaylist[_to] = e

						e = self.curPlaylist[_from].id
						self.curPlaylist[_from].id = self.curPlaylist[_to].id
						self.curPlaylist[_to].id = e

						_curPlaylist = []
						for i, e in enumerate(self.curPlaylist):
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
				
						e = self.curPlaylist[_from]
						self.curPlaylist[_from] = self.curPlaylist[_to]
						self.curPlaylist[_to] = e

						e = self.curPlaylist[_from].id
						self.curPlaylist[_from].id = self.curPlaylist[_to].id
						self.curPlaylist[_to].id = e
						
						_curPlaylist = []
						for i, e in enumerate(self.curPlaylist):
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
		for e in self.curPlaylist:
			self.presenter.mainPlaylistAddSong(ADD_END, False, "current", e)
	
	def openPlaylist(self):
		self.presenter.mainPlaylistOpen(self.curPlaylist)

	def addSong(self, play=True):
		e = self.curPlaylist[self.listPl._line]
		if play:
			self.presenter.player.stop()
		self.presenter.mainPlaylistAddSong(ADD_END, play, "current", e)
	
	def addSCSong(self, play=True):
		if not self.presenter.config.useInternet:
			return
		e = self.curPlaylist[self.listPl._line]
		playlistName = self.listPls._options[self.listPls._line][0][0]
		if playlistName == "SC:favorites":
			url = self.presenter.scGetStream(e.stream_url).location
			title = e.title
			fileName = e.title
			year = e.release_year
			globalId = e.id
			genre = e.genre
		else:
			url = self.presenter.scGetStream(e["stream_url"]).location
			title = e["title"]
			fileName = e["title"]
			year = e["release_year"]
			globalId = e["id"]
			genre = e["genre"]

		artist = song = title
		data = title.split(" - ")
		if len(data) < 2:
			pass
		else:
			artist = data[0].strip()
			song = data[1].strip()
		t = Tag()
		t.url = url
		t.artist = artist
		t.album = ''
		t.song = song
		t.fileName = fileName
		t.year = year
		t.genre = genre
		t.coverart = ''
		t.length = 0
		t.curLength = 0
		t.id = -1
		t.globalId = globalId
		self.presenter.mainPlaylistAddSong(ADD_END, play, "current", t)

	def updatePlaylists(self):
		pls = self.presenter.getListOfPlaylists()
		#print(pls)
		if pls == []:
			pass
		else:
			self.isSCPlaylist = False
			playlistName = pls[0]
			for i, e in enumerate(pls):
				pls[i] = ([e], i)

		useSC = True
		if not self.presenter.config.useInternet:
			useSC = False
		if useSC:
			if pls == []:
				playlistName = "SC:favorites"
				self.isSCPlaylist = True
			scList = ["SC:favorites"]

			scpls = self.presenter.scGetPlaylists()
			for p in scpls:
				scList += ["SC:"+p.title]

			for i, e in enumerate(scList):
				pls.append(([e], len(pls)))

		self.listPls._options = pls
		self.listPls.value = 0
		if playlistName[:3] == "SC:" and self.presenter.config.useInternet:
			self.isSCPlaylist = True
			_curPlaylist = []
			if playlistName == "SC:favorites":
				self.scpl = self.presenter.scGetFavorites()
				
				for i, e in enumerate(self.scpl):
					_curPlaylist.append((["-"+e.title], i))
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
				return
			else:
				scpls = self.presenter.scGetPlaylists()
				#print(scpls)
				scid = 0
				for p in scpls:
					
					if p.title == playlistName[3:]:
						scid = p.ud
						break
				self.scpl = self.presenter.scGetPlaylistsById(scid)
				for i, e in enumerate(self.scpl):
					_curPlaylist.append((["-"+e.title], i))
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
		if pls == []:
			return

		
		path = self.presenter.config.playlist_folder + "/"+ \
			playlistName if self.presenter.config.playlist_folder[len(self.presenter.config.playlist_folder)-1] != "/" else playlistName
		self.curPlaylist = loadPlaylist(path)
		_curPlaylist = []
		for i, e in enumerate(self.curPlaylist):
			_curPlaylist.append(([e.artist+" - "+e.song], i))
		self.listPl._options = _curPlaylist
		self.listPl.value = 0

	def setPresenter(self, p):
		self.presenter = p
		self.updatePlaylists()

	def _on_change(self):
		playlistName = self.listPls._options[self.listPls.value][0][0]

		if playlistName[:3] == "SC:" and self.presenter.config.useInternet:
			self.isSCPlaylist = True
			_curPlaylist = []
			if playlistName == "SC:favorites":
				self.curPlaylist = self.presenter.scGetFavorites()
				
				for i, e in enumerate(self.curPlaylist):
					_curPlaylist.append((["-"+e.title], i))
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
				return
			else:
				scpls = self.presenter.scGetPlaylists()
				scid = 0
				for p in scpls:
					if p.title == playlistName[3:]:
						scid = p.id
						break
				self.curPlaylist = self.presenter.scGetPlaylistById(scid).tracks
				for i, e in enumerate(self.curPlaylist):
					#print(e['title'])
					_curPlaylist.append((["-"+e['title']], i))
				self.listPl._options = _curPlaylist
				self.listPl.value = 0
				return
		self.isSCPlaylist = False
		path = self.presenter.config.playlist_folder + "/"+ \
			playlistName if self.presenter.config.playlist_folder[len(self.presenter.config.playlist_folder)-1] != "/" else playlistName
		self.curPlaylist = loadPlaylist(path)
		_curPlaylist = []
		for i, e in enumerate(self.curPlaylist):
			_curPlaylist.append(([e.artist+" - "+e.song], i))
		self.listPl._options = _curPlaylist
		self.listPl.value = 0