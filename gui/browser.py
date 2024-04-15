import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.widget import CustomFrame, CustomFileBrowser
from gui.utils.utils import getColor
from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.dialog import AddMusicDialog, ADD_END,ADD_BEGIN,ADD_AFTER,ADD_BEFORE

from strings import CURRENT_PLAYLIST
from gui.dialog_info import InfoDialog

class BrowserFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(BrowserFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Browser", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))

		self.addUpBar()
		
		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)

		self.browser = CustomFileBrowser(Widget.FILL_FRAME,
								 config.root_dir,
								 config,
								 name="browser",
								 on_select=self._play,
								 formats=[".mp3", ".flac", ".wav"])
		layout.add_widget(self.browser)
		self.addDownBar()
		
		self.fix()

	def process_event(self, event):
		# Do the key handling for this Frame.
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)
			if event.key_code in [ord('e')]:
				self.presenter.mainPlaylistAddSong(ADD_END, False, "current")
			if event.key_code in [ord('E')]:
				pls = self.presenter.getListOfPlaylists()
				for i, e in enumerate(pls):
					pls[i] = (e, i+1)
				pls = [(CURRENT_PLAYLIST, 0)] + pls
				self._scene.add_effect(
					AddMusicDialog(self._screen, 
						"Add song to playlist", 
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
						presenter=self.presenter, win="Browser"))
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

		return super(BrowserFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p

	def _addToPlaylist(self, selected):
		if selected == 0:
			self.presenter.mainPlaylistAddSong(self.browser.value)

	def _play(self):
		self.presenter.player.stop()
		self.presenter.mainPlaylistAddSong(ADD_END, True, "current")