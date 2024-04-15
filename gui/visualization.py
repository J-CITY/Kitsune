import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.utils import *
from tag_controller import Tag, getTagFromPath
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from gui.dialog import AddMusicDialog
from asciimatics.effects import Print, Clock
from gui.dialog_info import InfoDialog
from gui.utils.utils import getColor, getAttr
from gui.utils.widget import CustomVisualizer, CustomFrame, CustomFigletText
from asciimatics.renderers import Rainbow
from asciimatics.effects import Wipe

class VisualizationFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(VisualizationFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Visualizer", upBar=upBar, downBar=downBar, bg=getColor(config.bg_color))
		
		self.addUpBar()

		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)

		self.addDownBar()

		self.bgColor = getColor(config.clock.bg_color)
		self.viz = CustomVisualizer(self._canvas, config, self.dup, 
			self.ddown, color = "rainbow_p", bg=getColor(config.bg_color))
		self.add_effect(self.viz)

		self.fix()

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			if event.key_code in [ord(' ')]:
				self.viz.next()
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

			self.swichWindow(self.presenter, event)
			self.presenter.playerEventControl(event)

		return super(VisualizationFrame, self).process_event(event)
	
	def setPresenter(self, p):
		self.presenter = p
		self.viz.setPresenter(p)

	def _clear(self):
		pass

	def _update(self, frame_no):
		super(VisualizationFrame, self)._update(frame_no)
		if self.presenter != None and self._name != self.presenter.barGetFrameName():
			self.presenter.setFrameToBars(self._name)