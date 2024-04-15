import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils import *
from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.utils.utils import getColor, getAttr
from gui.utils.widget import CustomFigletText, CustomFrame
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog

class ClockFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(ClockFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Clock", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))

		self.addUpBar()

	
		self.addDownBar()

		_font = config.clock.type
		if _font == "digital":
			_font = config.clock.digital.font
		self.clock = CustomFigletText(self._canvas, self.dup, self.ddown, 
			config.clock.need_seconds, font=_font, config=config)
		self.add_effect(self.clock)
				#colour=7, attr=0, bg=0
		self.fix()

	def popup(self):
		pass
				
	def details(self):
		pass

	def process_event(self, event):
		# Do the key handling for this Frame.
		#self.__clear()
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			if event.key_code in [ord(" ")]:
				self.clock.needSeconds = not self.clock.needSeconds
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)

		return super(ClockFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p
