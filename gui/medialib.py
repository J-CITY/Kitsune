import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.widget import CustomFrame, CustomMultiColumnListBox
from gui.utils.utils import getAttr, ColorTheme, getColor

from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from gui.dialog import AddMusicDialog, ADD_END,ADD_BEGIN,ADD_AFTER,ADD_BEFORE
from strings import CURRENT_PLAYLIST
from gui.dialog_info import InfoDialog

class MedialibFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(MedialibFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Medialib", bg=getColor(config.bg_color))
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
		
		layout = Layout([1,1,1], fill_frame=True)
		self.add_layout(layout)

		c = config.medialib.color.split(':')
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.medialib.color_choice.split(':')
		self.color_choice = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.medialib.color_not_focus.split(':')
		self.color_not_focus = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		titleArtist = config.medialib.title_artist
		titleAlbum = config.medialib.title_album
		titleSong = config.medialib.title_song
		
		self.listArtists = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_choice],
			[],
			titles=[titleArtist],
			name="Artists", on_change=self._on_change_artist)
		self.listArtists.choiceCh = config.main_playlist.choice_char
		self.listArtists.itemCh = config.main_playlist.item_char
		layout.add_widget(self.listArtists, 0)

		self.listAlbums = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_not_focus],
			[],
			titles=[titleAlbum],
			name="Albums", on_change=self._on_change_album, on_select=self.openAlbum)
		self.listAlbums.choiceCh = config.main_playlist.choice_char
		self.listAlbums.itemCh = config.main_playlist.item_char
		layout.add_widget(self.listAlbums, 1)

		self.listSongs = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_not_focus],
			[],
			titles=[titleSong],
			name="Songs", on_select=self.addSong)
		self.listSongs.choiceCh = config.main_playlist.choice_char
		self.listSongs.itemCh = config.main_playlist.item_char
		layout.add_widget(self.listSongs, 2)

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
				if self.listSongs._has_focus:
					self.addSong(False)
				elif self.listAlbums._has_focus:
					self.presenter.mainPlaylistOpen(self.getCurrentAlbum())
					#self.presenter.medialibAddAlbum(ADD_END, False, "current")
			if event.key_code in [ord('E')]:
				name = ""
				title = ""
				if self.listSongs._has_focus:
					name = "Medialib"
					title = "Add song"
				elif self.listAlbums._has_focus:
					name = "MedialibAlbum"
					title = "Add album"
				if name != "":
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
							needNewPlaylist = True,
							needListAdd = True,
							needListPlaylists = True,
							needPlayCb = True,
							presenter=self.presenter, win=name))
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

		super(MedialibFrame, self).process_event(event)
		
		if self.listArtists._has_focus:
			self.listArtists._chColors = [self.color_choice]
		else:
			self.listArtists._chColors = [self.color_not_focus]
		if self.listAlbums._has_focus:
			self.listAlbums._chColors = [self.color_choice]
		else:
			self.listAlbums._chColors = [self.color_not_focus]
		if self.listSongs._has_focus:
			self.listSongs._chColors = [self.color_choice]
		else:
			self.listSongs._chColors = [self.color_not_focus]
		return

	def addSong(self, play=True):
		e = self.curPlaylist[self.listSongs._line]
		if play:
			self.presenter.player.stop()
		self.presenter.mainPlaylistAddSong(ADD_END, play, "current", e)

	def openAlbum(self):
		self.presenter.mainPlaylistOpen(self.getCurrentAlbum())
		self.presenter.playerPlayById(0)

	def setPresenter(self, p):
		self.presenter = p
		self.updateMl()

	def updateMl(self):
		self._set_artist()
		self._on_change_artist()
		self._on_change_album()

	def _set_artist(self):
		res = self.presenter.dbSelect("SELECT DISTINCT artist FROM medialib")
		res = sorted(res, key=lambda r: r[0])
		_curPlaylist = []
		for i, a in enumerate(res):
			_curPlaylist.append(([a[0]], i))
		self.listArtists._options = _curPlaylist
		self.listArtists.value = 0

	def _on_change_artist(self):
		res = self.presenter.dbExecute("SELECT DISTINCT album FROM medialib WHERE artist = ?",
			(self.listArtists._options[self.listArtists.value][0][0],))
		res = sorted(res, key=lambda r: r[0])
		_curPlaylist = []
		for i, a in enumerate(res):
			_curPlaylist.append(([a[0]], i))
		self.listAlbums._options = _curPlaylist
		self.listAlbums.value = 0
		self._on_change_album()

	def _on_change_album(self):
		res = self.presenter.dbExecute("SELECT * FROM medialib WHERE artist = ? AND album = ?",
			(self.listArtists._options[self.listArtists.value][0][0],
			self.listAlbums._options[self.listAlbums.value][0][0],))
		res = sorted(res, key=lambda r: r[2])
		self.curPlaylist = []
		_curPlaylist = []
		for i, a in enumerate(res):
			_curPlaylist.append(([a[2]], i))

			tag = Tag()
			tag.artist = a[0]
			tag.album = a[1]
			tag.song = a[2]
			tag.url = a[3]
			tag.year = a[4]
			tag.genre = a[5]
			tag.coverart = a[6]
			self.curPlaylist.append(tag)
		
		self.listSongs._options = _curPlaylist
		self.listSongs.value = 0

	def getCurrentTag(self):
		return self.curPlaylist[self.listSongs._line]
	
	def getCurrentAlbum(self):
		return self.curPlaylist