import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils import *
#from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from core.utils import getColor, getAttr
from gui.utils.widget import CustomFigletText, CustomFrame
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog
from core.strings import FRAME_CLOCK

#TODO: fix bug, when clock is last frame wrong graw down bar

class ClockFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(ClockFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name=FRAME_CLOCK, upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))

		self.addUpBar()
		self.addDownBar()

		_font = presenter.config.clock.type
		if _font == "digital":
			_font = presenter.config.clock.digital.font
		self.clock = CustomFigletText(self._canvas, self.dup, self.ddown, 
			presenter.config.clock.need_seconds, font=_font, config=presenter.config)
		self.add_effect(self.clock)
				#colour=7, attr=0, bg=0

		self.fix()
		self.setPresenter(presenter)

	def popup(self):
		pass

	def details(self):
		pass

	def process_event(self, event):
		# Do the key handling for this Frame.
		#self.__clear()
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord(" ")]:
				self.clock.needSeconds = not self.clock.needSeconds
			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)
		return super(ClockFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p
		self.presenter.addFrame(self.frameName, self)

