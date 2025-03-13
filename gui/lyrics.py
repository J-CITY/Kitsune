import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from core.tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock

from core.utils import getColor, getAttr, ColorTheme
from gui.utils.widget import CustomFrame, TextView
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog
import asyncio
from typing import NoReturn
from core.strings import FRAME_LYRICS

#TODO: cache
class LyricsFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(LyricsFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name=FRAME_LYRICS, upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))
		self.dup = len(upBar.layouts)
		self.ddown = len(downBar.layouts)
		self.artist = ""
		self.song = ""
		
		self.addUpBar()

		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)
		
		self.addDownBar()

		c = presenter.config.lyrics.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.text = TextView(self.screen.height-self.dup-self.ddown, tcolor, name="lyrics")
		layout.add_widget(self.text)

		self.lyricsCache = {}

		self.fix()
		self.setPresenter(presenter)
		#from PIL import Image
		#from term_image.image import AutoImage
		#img = Image.open("cache/in.jpg")
		#image = AutoImage(img)
		#image.height = 20
		#self.text.setText(str(image))

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
		self.presenter.addFrame(self.frameName, self)

	def setText(self, text):
		self.text.setText(text)

	def updateArtistSong(self):
		if self.presenter != None and \
			(self.artist != self.presenter.playerGetCurTag().artist\
			or self.song != self.presenter.playerGetCurTag().song):
			
			self.artist = self.presenter.playerGetCurTag().artist
			self.song = self.presenter.playerGetCurTag().song
		id = self.artist + self.song
		if id in self.lyricsCache:
			self.setText(self.lyricsCache[id])
			return True
		return False

	def updateLyricsCb(self, text, artist, song):
		self.lyricsCache[artist+song] = text
		if self.artist == artist and self.song == song:
			self.setText(text)
		else:
			self.presenter.lyricsUpdateText()
