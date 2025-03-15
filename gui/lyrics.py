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
from gui.utils.widget import CustomFrame, TextView, ImageView
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog
import asyncio
from typing import NoReturn
from core.strings import FRAME_LYRICS

class LyricsFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(LyricsFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name=FRAME_LYRICS, upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))
		self.dup = len(upBar.layouts)
		self.ddown = len(downBar.layouts)

		c = presenter.config.lyrics.color.split(':')
		self.tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.text = TextView(self.screen.height-self.dup-self.ddown, self.tcolor, name="lyrics")
		self.showImage = False
		self.image = ImageView(self.screen.height-self.dup-self.ddown, self.tcolor, name="art")
		self.image.screen = screen
		
		self.createLayout()

		self.lyricsCache = {}
		self.setPresenter(presenter)

	def createLayout(self):
		scrW = self.image.screen.width
		self.image.clear()
		self._layouts = []
		self.addUpBar()
		if self.showImage:
			col1sz = 20 + 5*2 if scrW > 20 + 5 * 2 else 0
			self.layout = Layout([col1sz, scrW - col1sz], fill_frame=True)
			self.add_layout(self.layout)
			self.layout.add_widget(self.image, 0)
			self.layout.add_widget(self.text, 1)
		else:
			self.layout = Layout([1], fill_frame=True)
			self.add_layout(self.layout)
			self.layout.add_widget(self.text, 0)
		self.addDownBar()
		self.fix()
		self.text.focus()

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			if event.key_code in [ord(' ')]:
				self.showImage = not self.showImage
				self.createLayout()
				return None
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
		if not self.presenter.song:
			return True
		id = self.presenter.song.artist + self.presenter.song.song
		if id in self.lyricsCache:
			self.setText(self.lyricsCache[id])
			return True
		return False

	def updateCover(self):
		if self.showImage == False:
			return True
		
		song = self.presenter.song
		if not song:
			return True

		path = "cache/" + song.artist + '_' + song.album + '_album.png'
		if os.path.exists(path):
			self.image.setImage(path, 20, 5, 5)
			return True
		return False

	def updateLyricsCb(self, text, artist, song):
		if text != '':
			self.lyricsCache[artist+song] = text
		if self.presenter.song and self.presenter.song.artist == artist and self.presenter.song.song == song:
			self.setText(text)
		else:
			self.presenter.lyricsUpdateText()

	def updateCoverCb(self, path, artist, song):
		if path == '':
			path = "cache/defAlbum.ico"
		if self.presenter.song and self.presenter.song.artist == artist and self.presenter.song.song == song:
			self.image.setImage(path, 20, 5, 5)
		else:
			self.presenter.lyricsUpdateCover()
