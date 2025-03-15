import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.utils.widget import CustomFrame, CustomMultiColumnListBox, CustomText
from core.utils import getAttr, ColorTheme, getColor, MusicAddPolitics

from core.tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from gui.dialog_download import DownloadDialog
from core.strings import CURRENT_PLAYLIST
from gui.dialog_info import InfoDialog

#TODO not now: create local favorite playlist

class SearchFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(SearchFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Search", upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))
		self.curDbPlaylist = []
		self.curYmPlaylist = []
		self.curDbPlaylistView = []
		self.curYmPlaylistView = []

		self.addUpBar()
		
		textLayout = Layout([90, 10], fill_frame=False)
		self.add_layout(textLayout)
		textLayout.add_widget(Button("OK", on_click=self._search), 1)
		
		c = presenter.config.search.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.searchText = CustomText(tcolor, label="Search:",
				name="search_text",
				validator="^[a-zA-Z0-9_]")
		textLayout.add_widget(self.searchText, 0)

		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)

		c = presenter.config.search.color.split(':')
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = presenter.config.search.color_choice.split(':')
		self.color_choice = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = presenter.config.search.color_not_focus.split(':')
		self.color_not_focus = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.titleDb = presenter.config.search.title_db
		self.titleYm = presenter.config.search.title_ym
		self.currentSearchTitle = self.titleDb

		self.listSearch = CustomMultiColumnListBox(
			Widget.FILL_FRAME,
			["<100%"],
			[self.color],
			[self.color_choice],
			[],
			titles=[self.currentSearchTitle],
			name="SearchDb", on_select=self.addSong)
		self.listSearch.choiceCh = presenter.config.search.choice_char
		self.listSearch.itemCh = presenter.config.search.item_char
		layout.add_widget(self.listSearch, 0)

		self.addDownBar()
		self.fix()
		self.setPresenter(presenter)

	def getCurTag(self):
		e = None
		if self.listSearchDb._has_focus:
			if self.currentSearchTitle == self.titleYm and len(self.curYmPlaylist) > 0:
				e = self.curYmPlaylist[self.listSearch._line]
			if self.currentSearchTitle == self.titleDb and len(self.curDbPlaylist) > 0:
				e = self.curDbPlaylist[self.listSearch._line]
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
								("At the end of playlist", MusicAddPolitics.ADD_END),
								("At the beginning of playlist", MusicAddPolitics.ADD_BEGIN),
								("After current song", MusicAddPolitics.ADD_AFTER),
								("Before current song", MusicAddPolitics.ADD_BEFORE)
							],
							playlistLists = pls,
							needNewPlaylist = True,
							needListAdd = True,
							needListPlaylists = True,
							needPlayCb = True,
							presenter=self.presenter, win=name))
				if event.key_code in [ord('L')]:
					if self.listSearch._has_focus and self.currentSearchTitle == self.titleYm:
						e = self.getCurTag()
						if e.globalId != -1:
							self.presenter.loadYandexMusicTrack(e.globalId)
				if event.key_code in [ord("i")]:
					self._scene.add_effect(
						InfoDialog(self._screen, 
							"Info",
							["OK"],
							config=self.presenter.config, win=self.frameName))
					
				if event.key_code in [ord("X")]:
					self.currentSearchTitle = self.titleDb if self.currentSearchTitle == self.titleYm else self.titleYm
					self.listSearch._titles = [self.currentSearchTitle]
					self.listSearch._options = self.curDbPlaylistView if self.currentSearchTitle == self.titleDb else self.curYmPlaylistView
					self.listSearch.value = 0

		super(SearchFrame, self).process_event(event)
		return

	def addSong(self, play=True):
		if self.listSearch._has_focus:
			if self.currentSearchTitle == self.titleYm and len(self.curYmPlaylist) > 0:
				e = self.curYmPlaylist[self.listSearch._line]
			if self.currentSearchTitle == self.titleDb and len(self.curDbPlaylist) > 0:
				e = self.curDbPlaylist[self.listSearch._line]
			if e:
				self.presenter.mainPlaylistAddSong(MusicAddPolitics.ADD_END, play, CURRENT_PLAYLIST, e)
		return

	def _search(self):
		searchText = self.searchText.value
		if searchText == "":
			return

		#search in db
		if self.currentSearchTitle == self.titleDb:
			res = self.presenter.dbSearch(searchText)
			res = sorted(res, key=lambda r: r[2])
			self.curDbPlaylist = []
			self.curDbPlaylistView = []
			for i, a in enumerate(res):
				self.curDbPlaylistView.append(([a[0]+" - "+a[2]], i))

				tag = Tag()
				tag.artist = a[0]
				tag.album = a[1]
				tag.song = a[2]
				tag.url = a[3]
				tag.year = a[4]
				tag.genre = a[5]
				tag.coverart = a[6]
				self.curDbPlaylist.append(tag)
			self.listSearch._options = self.curDbPlaylistView
			self.listSearch.value = 0
		else:
			self.presenter.searchYandexMusicTrack(searchText)

	def ymSearchCb(self, res, query):
		if query != self.searchText.value:
			return
		self.curYmPlaylist = []
		self.curYmPlaylistView = []
		for i, a in enumerate(res):
			self.curYmPlaylistView.append(([a['artists']+" - "+a['title']], i))
			tag = Tag()
			tag.artist = a['artists']
			tag.album = a['albums']
			tag.song = a['title']
			tag.url = ''
			tag.year = 0
			tag.genre = ''
			tag.coverart = ''
			tag.globalId = a['id']
			self.curYmPlaylist.append(tag)
		self.listSearch._options = self.curYmPlaylistView
		self.listSearch.value = 0

	def setPresenter(self, p):
		self.presenter = p
		self.presenter.addFrame(self.frameName, self)

