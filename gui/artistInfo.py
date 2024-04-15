import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock
from asciimatics.event import KeyboardEvent
from gui.utils.utils import getColor, getAttr, ColorTheme
from gui.utils.widget import CustomFrame, TextView
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog
import asyncio
from typing import NoReturn
from asciimatics.screen import Screen

class ArtistInfoFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(ArtistInfoFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="ArtistInfo", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))
		self.dup = 0
		self.ddown = 0
		self.artist = ""
		
		self.addUpBar()
		
		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)
		
		self.addDownBar()
		
		c = config.artist_info.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.text = TextView(self.screen.height-self.dup-self.ddown, tcolor, name="bio")
		layout.add_widget(self.text)
		self.fix()

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)
		return super(ArtistInfoFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p

	async def updateTextAsync(self, artist: str) -> NoReturn:
		text = self.presenter.lastfmGetCurArtistBio()
		if (self.artist == artist):
			self.text.setText(text)
		else:
			asyncio.run(self.updateTextAsync(self.artist))

	def updateText(self):
		if self.presenter != None and self.artist != self.presenter.playerGetCurTag().artist:
			self.artist = self.presenter.playerGetCurTag().artist
			#asyncio.run(self.updateTextAsync(self.artist))
			loop = asyncio.get_event_loop()
			loop.run_until_complete(self.updateTextAsync(self.artist))
