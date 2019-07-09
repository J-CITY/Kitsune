import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

import json
from collections import namedtuple
from asciimatics.widgets import *
from gui.utils.utils import ColorTheme, getColor, getAttr
from gui.utils.widget import CustomLabel

UP_BAR = 'up'
DOWN_BAR = 'down'


class Bar:
	def __init__(self):
		self.layouts =  []
		self.lables =  []
		

	def parse(self, jstr, b):
		self.start_char = jstr.bar.start_char
		self.prev_char = jstr.bar.prev_char
		self.next_char = jstr.bar.next_char
		self.cur_char = jstr.bar.cur_char
		self.end_char = jstr.bar.end_char

		if b == UP_BAR:
			bar = jstr.upBar
		else:
			bar = jstr.downBar

		for line in bar:
			layout = [line.left_size,
				line.centr_size,
				line.right_size]
			div = line.divider
			lw = CustomLabel(align=u'<', divider=div)
			for w in line.left:
				c = w.color.split(':')
				lw.addLable("",
					ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])),
					w.data
					)
			cw = CustomLabel(align=u'^', divider=div)
			for w in line.centr:
				c = w.color.split(':')
				cw.addLable("",
					ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])),
					w.data
					)
			rw = CustomLabel(align=u'>', divider=div)
			for w in line.right:
				c = w.color.split(':')
				rw.addLable("",
					ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])),
					w.data
					)
			self.layouts.append(layout)
			self.lables.append(lw)
			self.lables.append(cw)
			self.lables.append(rw)
			
	def update(self, tag):
		for l in self. lables:
			l.updateLable(tag, self.start_char, self.prev_char, self.cur_char, self.next_char, self.end_char)

	def setFrame(self, f):
		for l in self. lables:
			#print(l._frame._name, f._name)
			l._frame = f

	def getFrameName(self):
		if self.lables != []:
			return self.lables[0]._frame._name
		return None