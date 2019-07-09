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
from gui.dialog_info import InfoDialog
from gui.utils.utils import getColor, getAttr
from gui.utils.widget import CustomVisualizer, CustomFrame, CustomFigletText
from asciimatics.renderers import Rainbow
from asciimatics.effects import Wipe
class VisualizationFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(VisualizationFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Visualizer", bg=getColor(config.bg_color))
		self.upBar = upBar
		self.downBar = downBar
		self.dup = 0
		self.ddown = 0

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

		self.bgColor = getColor(config.clock.bg_color)
		self.viz = CustomVisualizer(self._canvas, config, self.dup, 
			self.ddown, color = "rainbow_p", bg=getColor(config.bg_color))
		self.add_effect(self.viz)
		
		#self.gbEffect = Wipe(screen, bg=1, stop_frame=screen.height * 2 + 30)
		#self.add_effect(self.gbEffect)

		self.presenter = None
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