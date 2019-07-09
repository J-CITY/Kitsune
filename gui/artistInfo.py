import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock

from gui.utils.utils import getColor, getAttr, ColorTheme
from gui.utils.widget import CustomFrame, TextView
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog

class ArtistInfoFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(ArtistInfoFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="ArtistInfo", bg=getColor(config.bg_color))
		self.upBar = upBar
		self.downBar = downBar
		self.dup = 0
		self.ddown = 0
		self.artist = ""

		dh = 0
		i = 0
		for l in upBar.layouts:
			_l = Layout([l[0],l[1],l[2]])
			self.add_layout(_l)
			_l.add_widget(upBar.lables[i], 0)
			_l.add_widget(upBar.lables[i+1], 1)
			_l.add_widget(upBar.lables[i+2], 2)
			i+=3
			dh+=1
			self.dup += 1
		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)
		i = 0
		for l in downBar.layouts:
			_l = Layout([l[0],l[1],l[2]])
			self.add_layout(_l)
			_l.add_widget(downBar.lables[i], 0)
			_l.add_widget(downBar.lables[i+1], 1)
			_l.add_widget(downBar.lables[i+2], 2)
			i+=3
			dh+=1
			self.ddown += 1
		
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

	def updateText(self):
		if self.presenter != None and \
			self.artist != self.presenter.playerGetCurTag().artist:
			
			text = self.presenter.lastfmGetCurArtistBio()
			self.text.setText(text)
			self.artist = self.presenter.playerGetCurTag().artist