import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock

from gui.utils.utils import getColor, getAttr, ColorTheme
from gui.utils.widget import CustomFrame, TextView
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog
import asyncio
from typing import NoReturn

class LyricsFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(LyricsFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Lyrics", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))
		self.dup = 0
		self.ddown = 0
		self.artist = ""
		self.song = ""
		
		self.addUpBar()

		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)
		
		self.addDownBar()

		c = config.lyrics.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.text = TextView(self.screen.height-self.dup-self.ddown, tcolor, name="lyrics")
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
		return super(LyricsFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p

	async def updateTextAsync(self, artist: str, song: str) -> NoReturn:
		text = self.presenter.lyricsGetSongLyrics(artist, song)
		if (self.artist == artist and self.song == song):
			self.text.setText(text)
		else:
			asyncio.run(self.updateTextAsync(self.artist, self.song))

	def updateText(self):
		if self.presenter != None and \
			(self.artist != self.presenter.playerGetCurTag().artist\
			or self.song != self.presenter.playerGetCurTag().song):
			
			self.artist = self.presenter.playerGetCurTag().artist
			self.song = self.presenter.playerGetCurTag().song

			asyncio.run(self.updateTextAsync(self.artist, self.song))
