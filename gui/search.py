import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.utils.widget import CustomFrame, CustomMultiColumnListBox, CustomText
from gui.utils.utils import getAttr, ColorTheme, getColor

from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from gui.dialog import AddMusicDialog, ADD_END,ADD_BEGIN,ADD_AFTER,ADD_BEFORE
from gui.dialog_download import DownloadDialog
from strings import CURRENT_PLAYLIST
from gui.dialog_info import InfoDialog

class SearchFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(SearchFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Search", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))
		self.curDbPlaylist = []
		self.curScPlaylist = []

		self.addUpBar()
		
		textLayout = Layout([90, 10], fill_frame=False)
		self.add_layout(textLayout)
		textLayout.add_widget(Button("OK", on_click=self._search), 1)
		
		c = config.search.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.searchText = CustomText(tcolor, label="Search:",
				name="search_text",
				validator="^[a-zA-Z0-9_]")
		textLayout.add_widget(self.searchText, 0)

		layout = Layout([1,1], fill_frame=True)
		self.add_layout(layout)

		c = config.search.color.split(':')
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.search.color_choice.split(':')
		self.color_choice = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.search.color_not_focus.split(':')
		self.color_not_focus = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		titleDb = config.search.title_db
		titleSc = config.search.title_sc
		
		
		self.listSearchDb = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_choice],
			[],
			titles=[titleDb],
			name="SearchDb", on_select=self.addSong)
		self.listSearchDb.choiceCh = config.search.choice_char
		self.listSearchDb.itemCh = config.search.item_char
		layout.add_widget(self.listSearchDb, 0)

		self.listSearchSc = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_not_focus],
			[],
			titles=[titleSc],
			name="SearchSc", on_select=self.addSong)
		self.listSearchSc.choiceCh = config.search.choice_char
		self.listSearchSc.itemCh = config.search.item_char
		layout.add_widget(self.listSearchSc, 1)

		self.addDownBar()
		self.fix()

	def getCurTag(self):
		e = None
		if self.listSearchDb._has_focus:
			if len(self.curDbPlaylist) > 0:
				e = self.curDbPlaylist[self.listSearchDb._line]
		if self.listSearchSc._has_focus:
			if len(self.curScPlaylist) > 0:
				e = self.curScPlaylist[self.listSearchSc._line]
		return e

	def process_event(self, event):
		# Do the key handling for this Frame.
		if isinstance(event, KeyboardEvent):
			if not self.searchText._has_focus:
				if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
					raise StopApplication("User quit")
				self.swichWindow(self.presenter, event)
				self.presenter.playerEventControl(event)
				if event.key_code in [ord('e')]:
					self.addSong(False)
				if event.key_code in [ord('E')]:
					name = "Search"
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
							needNewPlaylist = True,
							needListAdd = True,
							needListPlaylists = True,
							needPlayCb = True,
							presenter=self.presenter, win=name))
				if event.key_code in [ord('f')]:
					if self.listSearchSc._has_focus:
						if len(self.curScPlaylist) > 0:
							id = self.getCurTag().globalId
							self.presenter.scLike(id)
				if event.key_code in [ord('l')]:
					if self.listSearchSc._has_focus:
						e = self.getCurTag()
						if e != None:
							url = e.url
							name = e.fileName
							name = name.replace("\"", "")
							fpath = self.presenter.config.download_folder + "/" + name + ".mp3"
							self.presenter.scDownloadName(url, fpath, name)
							self.presenter.dbInsertByPath(fpath)
							self.presenter.medialibUpdate()
							tag = getTagFromPath(fpath)
							self.presenter.mainPlaylistAddSong(ADD_END, False, "current", tag)
				if event.key_code in [ord('L')]:
					if self.listSearchSc._has_focus:
						e = self.getCurTag()
						if e != None:
							url = e.url
							name = e.fileName
							name = name.replace("\"", "")
							self._scene.add_effect(
								DownloadDialog(self._screen, 
									"Download song", url, name+".mp3",
									["OK", "Cancel"],
									presenter=self.presenter, win="download_sc"))
				if event.key_code in [ord("i")]:
					self._scene.add_effect(
						InfoDialog(self._screen, 
							"Info",
							["OK"],
							config=self.presenter.config, win=self.frameName))

		super(SearchFrame, self).process_event(event)
		
		if self.listSearchDb._has_focus:
			self.listSearchDb._chColors = [self.color_choice]
		else:
			self.listSearchDb._chColors = [self.color_not_focus]
		if self.listSearchSc._has_focus:
			self.listSearchSc._chColors = [self.color_choice]
		else:
			self.listSearchSc._chColors = [self.color_not_focus]
		return

	def addSong(self, play=True):
		#e = self.curPlaylist[self.listSongs._line]
		#self.presenter.mainPlaylistAddSong(ADD_END, play, "current", e)
		if self.listSearchDb._has_focus:
			e = self.curDbPlaylist[self.listSearchDb._line]
			self.presenter.mainPlaylistAddSong(ADD_END, play, "current", e)
		if self.listSearchSc._has_focus:
			e = self.curScPlaylist[self.listSearchSc._line]
			self.presenter.mainPlaylistAddSong(ADD_END, play, "current", e)
		return

	def _search(self):
		searchText = self.searchText.value
		if searchText == "":
			return

		#search in db
		res = self.presenter.dbSearch(searchText)
		res = sorted(res, key=lambda r: r[2])
		self.curDbPlaylist = []
		_curPlaylist = []
		for i, a in enumerate(res):
			_curPlaylist.append(([a[0]+" - "+a[2]], i))

			tag = Tag()
			tag.artist = a[0]
			tag.album = a[1]
			tag.song = a[2]
			tag.url = a[3]
			tag.year = a[4]
			tag.genre = a[5]
			tag.coverart = a[6]
			self.curDbPlaylist.append(tag)
		self.listSearchDb._options = _curPlaylist
		self.listSearchDb.value = 0

		#search sc
		if self.presenter.config.useInternet:
			res = self.presenter.scSearch(searchText)
			res = self.presenter.scSearch(searchText)
			self.curScPlaylist = []
			_curPlaylist = []
			for i, a in enumerate(res):
				_curPlaylist.append(([a.title], i))
				artist = song = a.title
				data = a.title.split(" - ")
				if len(data) < 2:
					pass
				else:
					artist = data[0].strip()
					song = data[1].strip()
				tag = Tag()
				tag.artist = artist
				tag.album = ""
				tag.song = song
				tag.url = self.presenter.scGetStream(a.stream_url).location
				tag.year = a.release_year
				tag.genre = a.genre
				tag.coverart = ""
				tag.globalId = a.id
				tag.fileName = a.title
				self.curScPlaylist.append(tag)
			self.listSearchSc._options = _curPlaylist
			self.listSearchSc.value = 0

	def setPresenter(self, p):
		self.presenter = p
