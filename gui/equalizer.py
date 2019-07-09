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

from gui.utils.utils import getColor, getAttr, ColorTheme
from gui.utils.widget import (CustomFigletText, CustomFrame, 
	CustomLabel, CustomMultiColumnListBox, CustomCheckBox)
from asciimatics.renderers import Rainbow
from gui.dialog_info import InfoDialog

class EqualizerFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(EqualizerFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="Equalizer")
		self.upBar = upBar
		self.downBar = downBar
		self.dup = 0
		self.ddown = 0

		self.eqIsBass = False
		self.eqIsEcho = False
		self.eqIsChorus = False
		self.eqIsReverb = False
		self.eqIsFlange = False

		self.eqBass = [6, 5, 4]

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
		layout = Layout([1, 0.5], fill_frame=True)
		self.add_layout(layout)

		self.ch_less = config.equalizer.bar_less
		self.ch_more = config.equalizer.bar_more
		c = config.equalizer.color.split(':')
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		c = config.equalizer.color_choice.split(':')
		self.color_choice = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))

		lEq = CustomLabel(align=u'<')
		lEq.addLable("Equalizer",self.color,"%Equalizer")
		layout.add_widget(lEq)
		
		self.eqLevels = [80, 170, 310, 600, 1000, 3000, 6000, 10000, 12000, 14000]
		self.eqLevelsParam = [0, 0, 0 ,0, 0, 0, 0, 0, 0, 0]
		self.eqBars = []

		self.eqSpeedParam = 0
		# 80 170 310 600 1000 3000 6000 10000 12000 14000 Hz
		# "      -15               0          15"
		self.listEqBar = CustomMultiColumnListBox(
			11,
			["<100%"],
			[self.color],
			[self.color_choice],
			[],
			titles=["      -15           0             15"],
			name="eqBar")
		self.listEqBar.choiceCh = ''
		self.listEqBar.itemCh = ''
		layout.add_widget(self.listEqBar, 0)

		

		lEqSpeed = CustomLabel(align=u'<')
		lEqSpeed.addLable("Speed",self.color,"%Speed")
		layout.add_widget(lEqSpeed, 0)


		self.listEqSpeed = CustomMultiColumnListBox(
			2,
			["<100%"],
			[self.color],
			[self.color],
			[],
			titles=["      25 0                        400"],
			name="eqSpeed")
		self.listEqSpeed.choiceCh = ''
		self.listEqSpeed.itemCh = ''
		layout.add_widget(self.listEqSpeed, 0)
		#self.setEqSpeedParam()

		lEqPreset = CustomLabel(align=u'<')
		lEqPreset.addLable("Presets",self.color,"")
		layout.add_widget(lEqPreset, 1)


		self.eqPresets = []
		self.eqPresets.append(CustomCheckBox("Custom", self.color, name="CustomPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Default", self.color, name="DefaultPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Rock", self.color, name="RockPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Rap", self.color, name="RapPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Grunge", self.color, name="GrungePreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Metal", self.color, name="MetalPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Techno", self.color, name="TechnoPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Pop", self.color, name="PopPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Classic", self.color, name="ClassicPreset", on_change=self.__onChangePreset))
		self.eqPresets.append(CustomCheckBox("Voice", self.color, name="VoicePreset", on_change=self.__onChangePreset))
		for e in self.eqPresets:
			layout.add_widget(e, 1)
		self.eqPresets[1].value = True

		lEqEffects = CustomLabel(align=u'<')
		lEqEffects.addLable("Effects",self.color,"")
		layout.add_widget(lEqEffects, 1)

		self.eqBass = CustomCheckBox("BASS", self.color, name="BassPreset", on_change=self.__onChangeBass)
		layout.add_widget(self.eqBass, 1)
		self.eqEcho = CustomCheckBox("Echo", self.color, name="EchoPreset", on_change=self.__onChangeEcho)
		layout.add_widget(self.eqEcho, 1)

		self.eqFlange = CustomCheckBox("Flange", self.color, name="FlangePreset", on_change=self.__onChangeFlange)
		layout.add_widget(self.eqFlange, 1)
		self.eqChorus = CustomCheckBox("Chorus", self.color, name="ChorusPreset", on_change=self.__onChangeChorus)
		layout.add_widget(self.eqChorus, 1)
		self.eqReverb = CustomCheckBox("Reverb", self.color, name="ReverbPreset", on_change=self.__onChangeReverb)
		layout.add_widget(self.eqReverb, 1)

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
		
		self.fix()

	def popup(self):
		# Just confirm whenever the user actually selects something.
		print('')
				
	def details(self):
		# If python magic is installed, provide a little more detail of the current file.
		print('')
	def setEqBarParam(self):
		self.eqBars = []
		for i, l in enumerate(self.eqLevels):
			bar = ""
			for j in range (-15, 15):
				if j < self.eqLevelsParam[i]:
					bar += self.ch_less
				else:
					bar += self.ch_more
			title = str(self.eqLevels[i])
			title += ' '*(6-len(title)) 

			self.eqBars.append(([title + bar],i))

		self.listEqBar._options = self.eqBars
		self.presenter.eqSetLevelParam(self.eqLevelsParam)

	def setEqSpeedParam(self):
		self.eqSpeed = []
		bar = ""
		for j in range (-50, 415, 15):
			if j < self.eqSpeedParam:
				bar += self.ch_less
			else:
				bar += self.ch_more
		
		title = str(self.eqSpeedParam)
		title += ' '*(6-len(title)) 
		self.eqSpeed.append(([title + bar],0))

		self.listEqSpeed._options = self.eqSpeed
		self.presenter.eqSetSpeedParam(self.eqSpeedParam)

	def process_event(self, event):
		# Do the key handling for this Frame.
		#self.__clear()
		if isinstance(event, KeyboardEvent):
			if event.key_code == Screen.KEY_RIGHT:
				if self.listEqBar._has_focus:
					self.eqLevelsParam[self.listEqBar._line] = 15 if self.eqLevelsParam[self.listEqBar._line] == 15 else\
						self.eqLevelsParam[self.listEqBar._line] + 1
					self.setEqBarParam()
					for e in self.eqPresets:
						e.value = False
					self.eqPresets[0].value = True
				if self.listEqSpeed._has_focus:
					self.eqSpeedParam = 415 if self.eqSpeedParam + 10 >= 415 else\
						self.eqSpeedParam + 10
					self.setEqSpeedParam()
					for e in self.eqPresets:
						e.value = False
					self.eqPresets[0].value = True
				return
			if event.key_code == Screen.KEY_LEFT:
				if self.listEqBar._has_focus:
					self.eqLevelsParam[self.listEqBar._line] = -15 if self.eqLevelsParam[self.listEqBar._line] == -15 else\
						self.eqLevelsParam[self.listEqBar._line] - 1
					self.setEqBarParam()
				if self.listEqSpeed._has_focus:
					self.eqSpeedParam = -25 if self.eqSpeedParam-10 <= -25 else\
						self.eqSpeedParam - 10
					self.setEqSpeedParam()
				return
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
		
		super(EqualizerFrame, self).process_event(event)
		self.updateFocusColor()
		return
		
	def __onChangePreset(self):
		for e in self.eqPresets:
			if e._has_focus:
				text = e._text
				if e.value:
					self.eqLevelsParam = self.getPresetParam(text)
					self.setEqBarParam()
					for ee in self.eqPresets:
						if e != ee:
							ee.value = False
	def __onChangeBass(self):
		if self.eqBass.value:
			self.eqIsBass = True
		else:
			self.eqIsBass = False
		self.presenter.eqSetBassParam(self.eqIsBass)

	def __onChangeEcho(self):
		if self.eqEcho.value:
			self.eqIsEcho = True
		else:
			self.eqIsEcho = False
		self.presenter.eqSetEchoParam(self.eqIsEcho)

	def __onChangeFlange(self):
		if self.eqFlange.value:
			self.eqIsFlange = True
		else:
			self.eqIsFlange = False
		self.presenter.eqSetFlangeParam(self.eqIsFlange)
	def __onChangeChorus(self):
		if self.eqChorus.value:
			self.eqIsChorus = True
		else:
			self.eqIsChorus = False
		self.presenter.eqSetChorusParam(self.eqIsChorus)
	def __onChangeReverb(self):
		if self.eqReverb.value:
			self.eqIsReverb = True
		else:
			self.eqIsReverb = False
		self.presenter.eqSetReverbParam(self.eqIsReverb)

	def getPresetParam(self, param):
		return {
			"Custom": self.eqLevelsParam,
			"Default": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			"Rock": [-2, 1, 3, 7, -2, -2, 0, 0, 7, 7],
			"Rap": [-2, 0, 1, 7, -2, -2, 0, 0, 7, 9],
			"Grunge": [-5, 0, 0, -2, 0, 0, 2, 3, 0, -3],
			"Metal": [-5, 0, 0, 0, 0, 0, 3, 0, 3, 2],
			"Techno": [-7, 2, 4, -2, -2, -3, 0, 0, 5, 5],
			"Pop": [-1, 4, 5, 2, -1, -2, 0, 0, 4, 4],
			"Classic": [0, 0, 0, 4, 5, 3, 7, 3, 0, 0],
			"Voice": [-8, -6, -4, 1, 0, 0, 0, -4, -6, -8],
		}[param]

	def updateFocusColor(self):
		for e in self.eqPresets:
			if e._has_focus:
				e.color = self.color_choice
			else:
				e.color = self.color
		if self.listEqBar._has_focus:
			self.listEqBar._chColors = [self.color_choice]
		else:
			self.listEqBar._chColors = [self.color]
		if self.listEqSpeed._has_focus:
			self.listEqSpeed._chColors = [self.color_choice]
		else:
			self.listEqSpeed._chColors = [self.color]
		if self.eqBass._has_focus:
			self.eqBass.color = self.color_choice
		else:
			self.eqBass.color = self.color
		if self.eqEcho._has_focus:
			self.eqEcho.color = self.color_choice
		else:
			self.eqEcho.color = self.color

		if self.eqChorus._has_focus:
			self.eqChorus.color = self.color_choice
		else:
			self.eqChorus.color = self.color
		if self.eqReverb._has_focus:
			self.eqReverb.color = self.color_choice
		else:
			self.eqReverb.color = self.color
		if self.eqFlange._has_focus:
			self.eqFlange.color = self.color_choice
		else:
			self.eqFlange.color = self.color
	def setPresenter(self, p):
		self.presenter = p
		self.setEqBarParam()
		self.setEqSpeedParam()