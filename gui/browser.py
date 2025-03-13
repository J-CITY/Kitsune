import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.widget import CustomFrame, CustomFileBrowser
from core.utils import getColor, MusicAddPolitics
from core.tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.dialog import AddMusicDialog

from core.strings import CURRENT_PLAYLIST, FRAME_BROWSER, SONG_FORMATS
from gui.dialog_info import InfoDialog

class BrowserFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(BrowserFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name=FRAME_BROWSER, upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))

		self.addUpBar()

		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)

		self.browser = CustomFileBrowser(Widget.FILL_FRAME,
			presenter.getMusicRootFolder(),
			presenter.config,
			name="browser",
			on_select=self._play,
			formats=SONG_FORMATS)
		layout.add_widget(self.browser)
		self.addDownBar()
		self.fix()
		self.setPresenter(presenter)

	def process_event(self, event):
		# Do the key handling for this Frame.
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)
			if event.key_code in [ord('e')]:
				song = self.browser.value
				tag = getTagFromPath(song)
				if tag is not None:
					self.presenter.mainPlaylistAddSong(MusicAddPolitics.ADD_END, False, CURRENT_PLAYLIST, tag)
			if event.key_code in [ord('E')]:
				pls = [(CURRENT_PLAYLIST, 0)] + \
					[(e, i+1) for i, e in enumerate(self.presenter.getListOfPlaylists())]
				self._scene.add_effect(
					AddMusicDialog(self._screen, 
						"Add song to playlist", 
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
						presenter=self.presenter, win=FRAME_BROWSER))
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

		return super(BrowserFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p
		self.presenter.addFrame(self.frameName, self)

	def _play(self):
		self.presenter.playerStop()
		self.presenter.mainPlaylistAddSong(MusicAddPolitics.ADD_END, True, CURRENT_PLAYLIST)