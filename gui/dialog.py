import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.utils import ColorTheme, getColor, getAttr, ADD_END, ADD_BEGIN, ADD_AFTER, ADD_BEFORE
from gui.utils.widget import CustomText

class AddMusicDialog(Frame):

	def __init__(self, screen, text, buttons, 
			addList = [],
			playlistLists = [],
			needNewPlaylist = True,
			needListAdd = True,
			needListPlaylists = True,
			needPlayCb = True,
			presenter=None, on_close=None, has_shadow=False,
			win=""):
		self.presenter = presenter

		self._buttons = buttons
		self._on_close = on_close
		width = screen.width // 2

		self._message = text
		height = 17
		self.win = win
		# Construct the Frame
		self._data = {"message": self._message}
		super(AddMusicDialog, self).__init__(
			screen, height, width, self._data, has_shadow=has_shadow, is_modal=True)

		# Build up the message box
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		
		#TITLE
		if self._message != "":
			layout.add_widget(Label(self._message))
			layout.add_widget(Divider())

		self.playCb = None
		self.newPlaylist = None
		self.listPlaylists = None
		self.listAdd = None
		self.playlistLists = playlistLists
		self.addList = addList

		if needNewPlaylist:
			layoutText = Layout([1,1], fill_frame=False)
			self.add_layout(layoutText)
			c = presenter.config.dialog.color.split(':')
			tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			self.newPlaylist = CustomText(tcolor, label="New playlist:",
				name="CreatePlaylist",
				validator="^[a-zA-Z]")
			self.newPlaylist.value = ""
			layoutText.add_widget(self.newPlaylist, 0)
			if win == "MainPlaylist":
				layoutText.add_widget(Button("Add", on_click=self._addNewPlaylistAndSaveMainPlaylistBtn), 1)
			elif win == "Browser":
				layoutText.add_widget(Button("Add", on_click=self._addNewPlaylistAndSaveSongBtn), 1)
			elif win == "Medialib":
				layoutText.add_widget(Button("Add", on_click=self._addNewPlaylistAndSaveSongBtn), 1)
			elif win == "MedialibAlbum":
				layoutText.add_widget(Button("Add", on_click=self._addNewPlaylistAndSaveMainPlaylistBtn), 1)
			elif win == "Search":
				layoutText.add_widget(Button("Add", on_click=self._addNewPlaylistAndSaveSongBtn), 1)

			layoutText.add_widget(Divider(), 0)
			layoutText.add_widget(Divider(), 1)
		if needListPlaylists:
			layoutAdd = Layout([1], fill_frame=False)
			self.add_layout(layoutAdd)
			self.listPlaylists = ListBox(5, playlistLists, on_change=self._on_change_playlist)
			self.listPlaylists.value = 0
			layoutAdd.add_widget(self.listPlaylists)
			layoutAdd.add_widget(Divider())
		if needListAdd:
			layoutAdd = Layout([1], fill_frame=False)
			self.add_layout(layoutAdd)
			self.listAdd = ListBox(5, addList)
			self.listAdd.value = 0
			layoutAdd.add_widget(self.listAdd)
			layoutAdd.add_widget(Divider())
		if needPlayCb:
			layoutAdd = Layout([1], fill_frame=False)
			self.add_layout(layoutAdd)
			self.playCb = CheckBox("",
				label="Play?",
				name="Need Play")
			layoutAdd.add_widget(self.playCb)
			layoutAdd.add_widget(Divider())

		layoutBtns = Layout([1 for _ in buttons])
		self.add_layout(layoutBtns)
		for i, button in enumerate(buttons):
			func = partial(self._destroy, i)
			layoutBtns.add_widget(Button(button, func), i)
		self.fix()

	def _destroy(self, selected):
		if selected == 0:
			pcb = False
			if self.playCb != None and not self.playCb.disabled:
				pcb = self.playCb.value

			if self.win == "Playlists":
				self.presenter.playlistAddPlaylist(self.listAdd.value, #pos, pl name
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
			elif self.win == "Playlist":
				self.presenter.playlistAddSong(self.listAdd.value, 
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
			elif self.win == "MainPlaylist":
				self.presenter.playlistAddPlaylist(self.listAdd.value, #pos, pl name
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
			elif self.win == "Browser":
				self.presenter.mainPlaylistAddSong(self.listAdd.value, 
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
			elif self.win == "Medialib":
				self.presenter.medialibAddSong(self.listAdd.value, 
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
			elif self.win == "MedialibAlbum":
				self.presenter.medialibAddAlbum(self.listAdd.value, 
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
			elif self.win == "Search":
				self.presenter.searchAddSong(self.listAdd.value, 
					pcb, self.listPlaylists._options[self.listPlaylists._line][0])
		self._scene.remove_effect(self)
		if self._on_close:
			self._on_close(-1)

	# create new playlist
	def _addNewPlaylistAndSaveSongBtn(self):
		if self.newPlaylist.value == "current" or self.newPlaylist.value == "":
			self.newPlaylist.value = ""
			return
		if self.win == "Medialib":
			self.presenter.medialibCreateNewPlaylistAndSaveSong(self.newPlaylist.value)
		elif self.win == "Browser":
			self.presenter.createNewPlaylistAndSaveSong(self.newPlaylist.value)
		self._scene.remove_effect(self)
		if self._on_close:
			self._on_close(-1)
	
	def _addNewPlaylistAndSaveMainPlaylistBtn(self):
		#if new pl name == current or empty
		if self.newPlaylist.value == "current" or self.newPlaylist.value == "":
			self.newPlaylist.value = ""
			return
		#save pl
		if self.win == "MainPlaylist":
			self.presenter.createNewPlaylistAndSaveMainPlaylist(self.newPlaylist.value)
		elif self.win == "MedialibAlbum":
			self.presenter.medialibCreateNewPlaylistAlbum(self.newPlaylist.value)
		elif self.win == "Search":
			self.presenter.createNewPlaylistFromSearch(self.newPlaylist.value)
		#and exit
		self._scene.remove_effect(self)
		self.presenter.playlistsUpdatePlaylists()
		if self._on_close:
			self._on_close(-1)

	def _on_change_playlist(self):
		if self.listAdd != None and self.listPlaylists != None and \
			self.listPlaylists._options[self.listPlaylists._line][0] == "current": #is current
			if self.playCb != None:
				self.playCb.disabled = False
			self.listAdd._options = self.addList
			self.listAdd._line = 0
		elif self.listAdd != None and self.listPlaylists != None:
			if self.playCb != None:
				self.playCb.disabled = True
			options = []
			for i, p in enumerate(self.addList):
				if p[1] < 2:
					options.append(p)
			self.listAdd._options = options
			self.listAdd._line = 0
