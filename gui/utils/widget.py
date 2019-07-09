import os, sys
parentPath = os.path.abspath("../../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from asciimatics.event import KeyboardEvent
from asciimatics.widgets import *
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.renderers import StaticRenderer
from abc import ABCMeta, abstractmethod, abstractproperty

from enum import Enum
from math import sin, cos, pi, sqrt, log, exp

from pyfiglet import Figlet, DEFAULT_FONT
from asciimatics.renderers import FigletText

from gui.utils.utils import getColor, getAttr, ColorTheme, split_text
import datetime
from player import (MOD_ONE_SONG,MOD_SONG_CIRCLE,MOD_ONE_PLAYLIST,
	MOD_PLAYLIST_CIRCLE,MOD_PLAYLIST_RANDOM)

class CustomLabel(Widget):
	def __init__(self, height=1, align="<", divider=' '):
		super(CustomLabel, self).__init__(None, tab_stop=False)

		self._required_height = height
		self._align = align
		
		self.labels = []
		self.colors = []
		self.tags = []
		self.needUpdate = False
		self.divider = divider


	def process_event(self, event):
		return event

	def getMode(self, mode, cf):
		_str = ""

		if cf:
			_str+="-c-"
		if mode == MOD_ONE_SONG:
			_str+="-)-"
		elif mode == MOD_SONG_CIRCLE:
			_str+="()-"
		elif mode == MOD_ONE_PLAYLIST:
			_str+="->-"
		elif mode == MOD_PLAYLIST_CIRCLE:
			_str+="<>-"
		elif mode == MOD_PLAYLIST_RANDOM:
			_str+="-R-"
		return _str


	def update(self, frame_no):
		if self.needUpdate:
			self.needUpdate = False
			i = 0
			for t in self.tags:
				if len(t) > 0 and t[0]=='%':
					self.labels[i] = t[1:]
				elif t == "progress":
					self.labels[i] = self.getProgress(self.tag["curLength"], self.tag["length"], self.start_char, 
							self.prev_char, self.cur_char, self.next_char, self.end_char)
				elif t == "mode":
					self.labels[i] = self.getMode(self.tag["mode"], self.tag["crossfade"])
				elif t == "curLength" or t == "length":
					res = str(datetime.timedelta(seconds=self.tag[t]))
					_res = res.split(':')
					res = _res[1]+":"+_res[2]
					if _res[0] != "0":
						res = _res[0]+":"+res
					self.labels[i] = res
				else:
					self.labels[i] = str(self.tag[t])
				i+=1

		fulllen = 0
		for _text in self.labels:
			fulllen += len(_text)
		fulllen = min(self._w, fulllen)
		ii = 0
		if self._align == u"<":
			for (j, _text) in enumerate(self.labels):
				colour = self.colors[j].color
				attr = self.colors[j].attr
				bg = self.colors[j].bg
				l = len(_text)
				self._frame.canvas.paint(
					"{:{}{}}".format(_text, "<", self._w), self._x+ii, self._y, colour, attr, bg)
				ii += l
			if self.colors != []:
				j = len(self.labels)-1
				colour = self.colors[j].color
				attr = self.colors[j].attr
				bg = self.colors[j].bg
				self._frame.canvas.paint(
						"{:{}{}}".format(self.divider*self._w, "<", self._w), self._x+ii, self._y, colour, attr, bg)
		elif self._align == u">":
			if self.colors != []:
				colour = self.colors[0].color
				attr = self.colors[0].attr
				bg = self.colors[0].bg
				self._frame.canvas.paint(
						"{:{}{}}".format(self.divider*(self._x+ self._w-fulllen), "<", (self._x+ self._w-fulllen)), 
							self._x, self._y, colour, attr, bg)
			for (j, _text) in enumerate(self.labels):
				colour = self.colors[j].color
				attr = self.colors[j].attr
				bg = self.colors[j].bg
				l = len(_text)
				self._frame.canvas.paint(
					"{:{}{}}".format(_text, "<", l), self._x + self._w-fulllen+ii, self._y, colour, attr, bg)
				ii += l
		elif self._align == u"^":
			start = (self._w-fulllen) // 2 + 1
			for (j, _text) in enumerate(self.labels):
				colour = self.colors[j].color
				attr = self.colors[j].attr
				bg = self.colors[j].bg
				l = len(_text)
				self._frame.canvas.paint(
					"{:{}{}}".format(_text, "<", l), self._x+start+ii, self._y, colour, attr, bg)
				ii += l
			if self.colors != []:
				colour = self.colors[0].color
				attr = self.colors[0].attr
				bg = self.colors[0].bg
				self._frame.canvas.paint(
					"{:{}{}}".format(self.divider*start, "<", start), self._x, self._y, colour, attr, bg)
				j=len(self.colors)-1
				colour = self.colors[j].color
				attr = self.colors[j].attr
				bg = self.colors[j].bg
				self._frame.canvas.paint(
					"{:{}{}}".format(self.divider*start, "<", start), self._x+start+ii, self._y, colour, attr, bg)

	def reset(self):
		pass

	def required_height(self, offset, width):
		# Allow one line for text and a blank spacer before it.
		return self._required_height

	def addLable(self, label, color, tag):
		self.labels.append(label)
		self.colors.append(color)
		self.tags.append(tag)

	@property
	def text(self):
		return self.labels

	@text.setter
	def text(self, new_value):
		self.labels = new_value

	@property
	def value(self):
		return self._value

	def updateLable(self, tag, start_char, prev_char, cur_char, next_char, end_char):
		self.needUpdate = True
		
		self.tag = tag
		self.start_char = start_char
		self.prev_char = prev_char
		self.cur_char = cur_char
		self.next_char = next_char
		self.end_char = end_char
	
	def getProgress(self, cur, length, start_char, prev_char, cur_char, next_char, end_char):
		res = start_char
		if length == 0:
			pos = 0
		else:
			pos = int(cur*self._w/length)
		for i in range(0, self._w):
			if (i < pos):
				res += prev_char
			if (i > pos):
				res += next_char
			if (i == pos):
				res += cur_char
		if end_char != '':
			res[len(res)-1] = end_char
		return res
	#def frame_update_count(self):
	#	super(CustomLabel, self).frame_update_count()
	#	return 1

class _BaseListBox(with_metaclass(ABCMeta, Widget)):

	def __init__(self, height, options, titles=None, label=None, name=None, on_change=None,
				 on_select=None, validator=None):
		super(_BaseListBox, self).__init__(name)
		self._options = options
		self._titles = titles
		self._label = label
		self._line = 0
		self._start_line = 0
		self._required_height = height
		self._on_change = on_change
		self._on_select = on_select
		self._validator = validator
		self._search = ""
		self._last_search = datetime.datetime.now()
		self._scroll_bar = None

	def reset(self):
		pass

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if len(self._options) > 0 and event.key_code == Screen.KEY_UP:
				# Move up one line in text - use value to trigger on_select.
				self._line = max(0, self._line - 1)
				self.value = self._options[self._line][1]
			elif len(self._options) > 0 and event.key_code == Screen.KEY_DOWN:
				# Move down one line in text - use value to trigger on_select.
				self._line = min(len(self._options) - 1, self._line + 1)
				self.value = self._options[self._line][1]
			elif len(self._options) > 0 and event.key_code == Screen.KEY_PAGE_UP:
				# Move up one page.
				self._line = max(0, self._line - self._h + (1 if self._titles else 0))
				self.value = self._options[self._line][1]
			elif len(self._options) > 0 and event.key_code == Screen.KEY_PAGE_DOWN:
				# Move down one page.
				self._line = min(
					len(self._options) - 1, self._line + self._h - (1 if self._titles else 0))
				self.value = self._options[self._line][1]
			elif event.key_code in [Screen.ctrl("m"), Screen.ctrl("j")]:
				# Fire select callback.
				if self._on_select:
					self._on_select()
			elif event.key_code > 0:
				# Treat any other normal press as a search
				now = datetime.datetime.now()
				if now - self._last_search >= timedelta(seconds=1):
					self._search = ""
				self._search += chr(event.key_code)
				self._last_search = now

				# If we find a new match for the search string, update the list selection
				new_value = self._find_option(self._search)
				if new_value is not None:
					self.value = new_value
			else:
				return event
		elif isinstance(event, MouseEvent):
			# Mouse event - adjust for scroll bar as needed.
			if event.buttons != 0:
				# Check for normal widget.
				if (len(self._options) > 0 and
						self.is_mouse_over(event, include_label=False)):
					# Figure out selected line
					new_line = event.y - self._y + self._start_line
					if self._titles:
						new_line -= 1
					new_line = min(new_line, len(self._options) - 1)

					# Update selection and fire select callback if needed.
					if new_line >= 0:
						self._line = new_line
						self.value = self._options[self._line][1]
						if event.buttons & MouseEvent.DOUBLE_CLICK != 0 and self._on_select:
							self._on_select()
					return None

				# Check for scroll bar interactions:
				if self._scroll_bar:
					event = self._scroll_bar.process_event(event)

			# Ignore other mouse events.
			return event
		else:
			# Ignore other events
			return event

		# If we got here, we processed the event - swallow it.
		return None

	@abstractmethod
	def _find_option(self, search_value):
		pass

	def required_height(self, offset, width):
		return self._required_height

	@property
	def start_line(self):
		return self._start_line

	@start_line.setter
	def start_line(self, new_value):
		if 0 <= new_value < len(self._options):
			self._start_line = new_value

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, new_value):
		# Only trigger change notification after we've changed selection
		old_value = self._value
		self._value = new_value
		for i, [_, value] in enumerate(self._options):
			if value == new_value:
				self._line = i
				break
		else:
			# No matching value - pick a default.
			if len(self._options) > 0:
				self._line = 0
				self._value = self._options[self._line][1]
			else:
				self._line = -1
				self._value = None
		if self._validator:
			self._is_valid = self._validator(self._value)
		if old_value != self._value and self._on_change:
			self._on_change()

		# Fix up the start line now that we've explicitly set a new value.
		self._start_line = max(
			0, max(self._line - self._h + 1, min(self._start_line, self._line)))

	@property
	def options(self):
		return self._options

	@options.setter
	def options(self, new_value):
		self._options = new_value
		self.value = self._options[0][1] if len(self._options) > 0 else None

def _enforce_width(text, width, unicode_aware=True):
	size = 0
	if unicode_aware:
		for i, c in enumerate(text):
			if size + wcwidth(c) > width:
				return text[0:i]
			size += wcwidth(c)
	elif len(text) + 1 > width:
		return text[0:width]
	return text

class CustomMultiColumnListBox(_BaseListBox):
	def __init__(self, height, columns, colors, chColors, options, titles=None, label=None,
				 name=None, on_change=None, on_select=None):
		super(CustomMultiColumnListBox, self).__init__(
			height, options, titles=titles, label=label, name=name, on_change=on_change,
			on_select=on_select)
		self._columns = []
		self._colors = []
		self._align = []
		self._spacing = []
		self._chColors = []
		for i, column in enumerate(columns):
			if isinstance(column, int):
				self._columns.append(column)
				self._align.append("<")
			else:
				match = re.match(r"([<>^]?)(\d+)([%]?)", column)
				self._columns.append(float(match.group(2)) / 100
									 if match.group(3) else int(match.group(2)))
				self._align.append(match.group(1) if match.group(1) else "<")
			self._spacing.append(1 if i > 0 and self._align[i] == "<" and
								 self._align[i - 1] == ">" else 0)
		for color in colors:
			self._colors.append(color)
		for color in chColors:
			self._chColors.append(color)
		self.choiceCh = ''
		self.itemCh = ''
		self._offset = 0
		

	def _get_width(self, width):
		if isinstance(width, float):
			return int(self._w * width)
		if width == 0:
			width = (self._w - sum(self._spacing) -
					 sum([self._get_width(x) for x in self._columns if x != 0]))
		return width

	def update(self, frame_no):
		self._draw_label()
		# Calculate new visible limits if needed.
		height = self._h
		dx = dy = 0

		start = 0
		for j, [title, align, space] in enumerate(
					zip(self._titles, self._align, self._spacing)):
			colour = self._colors[j].color
			attr = self._colors[j].attr
			bg = self._colors[j].bg
			width = self._get_width(self._columns[j])
			for i in range(height):
				self._frame.canvas.print_at(
					" " * (width+space),
					self._x+start,
					self._y + i + dy,
					colour, attr, bg)
			start += (width+space)
		# Allow space for titles if needed.
		if self._titles:
			dy += 1
			height -= 1
			row_dx = 0
			
			for i, [title, align, space] in enumerate(
					zip(self._titles, self._align, self._spacing)):
				width = self._get_width(self._columns[i])
				colour = self._colors[i].color
				attr = self._colors[i].attr
				bg = self._colors[i].bg
				self._frame.canvas.print_at(
					"{}{:{}{}}".format(" " * space,
									_enforce_width(
										title, width, self._frame.canvas.unicode_aware),
									align, width),
					self._x + self._offset + row_dx,
					self._y,
					colour, attr, bg)
				row_dx += width + space

		# Don't bother with anything else if there are no options to render.
		if len(self._options) <= 0:
			return
		# Render visible portion of the text.
		self._start_line = max(0, max(self._line - height + 1,
									  min(self._start_line, self._line)))
		for i, [row, _] in enumerate(self._options):
			if self._start_line <= i < self._start_line + height:
				#colour, attr, bg = self._pick_colours("field", i == self._line)
				
				row_dx = 0
				ii = 0
				for text, width, align, space in zip_longest(
						row, self._columns, self._align, self._spacing, fillvalue=""):
					if i == self._line:
						colour = self._chColors[ii].color
						attr = self._chColors[ii].attr
						bg = self._chColors[ii].bg
						ch = self.choiceCh
					else:
						colour = self._colors[ii].color
						attr = self._colors[ii].attr
						bg = self._colors[ii].bg
						ch = self.itemCh
					if ii != 0:
						ch = ''
					ii+=1
					if width == "":
						break
					width = self._get_width(width)
					if len(text) > width:
						text = text[:width - 3] + "..."
					
					self._frame.canvas.print_at(
						"{}{:{}{}}".format(" " * space,
											_enforce_width(
												ch + text, width, self._frame.canvas.unicode_aware),
											align, width),
						self._x + self._offset + dx + row_dx,
						self._y + i + dy - self._start_line,
						colour, attr, bg)
					row_dx += width + space

	def _find_option(self, search_value):
		for row, value in self._options:
			# TODO: Should this be aware of a sort column?
			if row[0].startswith(search_value):
				return value
		return None

class CustomMainPlaylistBox(CustomMultiColumnListBox):
	def __init__(self, height, columns, colors, chColors, playColors, data,
				options, titles=None, label=None,
				name=None, on_change=None, on_select=None):
		super(CustomMainPlaylistBox, self).__init__(
			height, columns, colors, chColors, options, titles, label,
			name, on_change, on_select)
		self.playCh = ''
		self.playId = -10
		self._playColors = []
		self._data = []
		for color in playColors:
			self._playColors.append(color)
		for d in data:
			self._data.append(d)

	def update(self, frame_no):
		self._draw_label()

		# Calculate new visible limits if needed.
		height = self._h
		dx = dy = 0

		start = 0
		for j, [title, align, space] in enumerate(
					zip(self._titles, self._align, self._spacing)):
			colour = self._colors[j].color
			attr = self._colors[j].attr
			bg = self._colors[j].bg
			width = self._get_width(self._columns[j])
			for i in range(height):
				self._frame.canvas.print_at(
					" " * (width+space),
					self._x+start,
					self._y + i + dy,
					colour, attr, bg)
			start += (width+space)
		# Allow space for titles if needed.
		if self._titles:
			dy += 1
			height -= 1
			row_dx = 0
			
			for i, [title, align, space] in enumerate(
					zip(self._titles, self._align, self._spacing)):
				width = self._get_width(self._columns[i])
				colour = self._colors[i].color
				attr = self._colors[i].attr
				bg = self._colors[i].bg
				self._frame.canvas.print_at(
					"{}{:{}{}}".format(" " * space,
									   _enforce_width(
										   title, width, self._frame.canvas.unicode_aware),
									   align, width),
					self._x + self._offset + row_dx,
					self._y,
					colour, attr, bg)
				row_dx += width + space

		# Don't bother with anything else if there are no options to render.
		if len(self._options) <= 0:
			return

		# Render visible portion of the text.
		self._start_line = max(0, max(self._line - height + 1,
									  min(self._start_line, self._line)))
		for i, [row, _] in enumerate(self._options):
			if self._start_line <= i < self._start_line + height:
				#colour, attr, bg = self._pick_colours("field", i == self._line)
				
				row_dx = 0
				ii = 0
				for text, width, align, space in zip_longest(
						row, self._columns, self._align, self._spacing, fillvalue=""):
					if i == self._line:
						colour = self._chColors[ii].color
						attr = self._chColors[ii].attr
						bg = self._chColors[ii].bg
						ch = self.choiceCh
					elif i == self.playId:
						colour = self._playColors[ii].color
						attr = self._playColors[ii].attr
						bg = self._playColors[ii].bg
						ch = self.playCh
					else:
						colour = self._colors[ii].color
						attr = self._colors[ii].attr
						bg = self._colors[ii].bg
						ch = self.itemCh
					if ii != 0:
						ch = ''
					ii+=1
					if width == "":
						break
					width = self._get_width(width)
					if len(text) > width:
						text = text[:width - 3] + "..."
					self._frame.canvas.print_at(
						"{}{:{}{}}".format(" " * space,
											_enforce_width(
												ch + text, width, self._frame.canvas.unicode_aware),
											align, width),
						self._x + self._offset + dx + row_dx,
						self._y + i + dy - self._start_line,
						colour, attr, bg)
					row_dx += width + space
	
	def clone(self, new_widget):
		#new_widget._populate_list(self._root)
		new_widget._start_line = self._start_line
		new_widget._line = self._line
		#new_widget._root = self._root
		new_widget.value = self.value
		new_widget._options = self._options

	def addItemsBack(self, tags):
		for tag in tags:
			res = []
			for d in self._data:
				res.append(str(tag[d]))
			self._options.append((res, tag['id']))
			if self._line < 0 and len(self._options) > 0:
				self._line = 0
	def updateList(self, newList):
		resList = []
		for e in newList:
			res = []
			for d in self._data:
				res.append(str(e.get(d)))
			resList.append((res, e.get('id')))
		self._options = resList
	
class CustomFileBrowser(CustomMultiColumnListBox):
	def __init__(self, height, root, config, 
		name=None, on_select=None, on_change=None, formats=[], onlyDir=False):

		c = config.browser.color.split(':')
		cc = config.browser.color_choice.split(':')
		super(CustomFileBrowser, self).__init__(
			height,
			["<90%", ">10"],
			[ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])),
				ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))],
			[ColorTheme(getColor(cc[0]), getAttr(cc[1]), getColor(cc[2])),
				ColorTheme(getColor(cc[0]), getAttr(cc[1]), getColor(cc[2]))],
			[],
			titles=["Filename", "Size"],
			name=name,
			on_select=self._on_select,
			on_change=on_change)

		self._external_notification = on_select
		self._root = root
		self._in_update = False
		self._initialized = False

		self.dirCh = config.browser.dir_char
		self.fileCh = config.browser.file_char
		self.choiceCh = config.browser.choice_char
		self.itemCh = config.browser.item_char
		self.color = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.choiceColor = ColorTheme(getColor(cc[0]), getAttr(cc[1]), getColor(cc[2]))
		self.formats = formats
		self.onlyDir = onlyDir

	def update(self, frame_no):
		if not self._initialized:
			self._populate_list(self._root)
			self._initialized = True
		super(CustomFileBrowser, self).update(frame_no)

	def _on_select(self):
		if self.value and os.path.isdir(self.value):
			self._populate_list(self.value)
		elif self._external_notification:
			self._external_notification()

	def clone(self, new_widget):
		new_widget._populate_list(self._root)
		new_widget._start_line = self._start_line
		new_widget._root = self._root
		new_widget.value = self.value

	def _populate_list(self, value):
		if value is None:
			return

		# Stop any recursion - no more returns from here to end of fn please!
		if self._in_update:
			return
		self._in_update = True

		# We need to update the tree view.
		self._root = os.path.abspath(value if os.path.isdir(value) else os.path.dirname(value))

		tree_view = []
		if len(self._root) > len(os.path.abspath(os.sep)):
			tree_view.append(([self.dirCh+".."], os.path.join(self._root, "..")))

		tree_dirs = []
		tree_files = []
		files = os.listdir(self._root)
		for my_file in files:
			full_path = os.path.join(self._root, my_file)
			details = os.stat(full_path)
			if os.path.isdir(full_path):
				tree_dirs.append(([self.dirCh+"{}".format(my_file),
								   ""], full_path))
			else:
				_, ext = filename, file_extension = os.path.splitext(full_path)
				if ext.lower() in self.formats:
					tree_files.append(([self.fileCh+"{}".format(my_file),
									readable_mem(details.st_size)], full_path))

		tree_view.extend(sorted(tree_dirs))
		if not self.onlyDir:
			tree_view.extend(sorted(tree_files))

		self.options = tree_view
		self._titles[0] = self._root

		# We're out of the function - unset recursion flag.
		self._in_update = False
	def getDir(self):
		return self._root
	
class CustomFrame(Frame):
	def __init__(self, screen, height, width, has_border, name, bg=0):
		self.bgColor = bg
		self.frameName = name
		super(CustomFrame, self).__init__(
			screen, height, width, has_border=has_border, name=name)
	@property
	def frame_update_count(self):
		return 1
	def _clear(self):
		for y in range(self._canvas._buffer_height):
			self._canvas.print_at(
				" " * self._canvas.width, 0, y, 0, 0, self.bgColor)
	def swichWindow(self, presenter, event):
		from asciimatics.exceptions import NextScene
		if event.key_code in [ord('1')]:
			presenter.setFrameToBars("MainPlaylist")
			raise NextScene("MainPlaylist")
		elif event.key_code in [ord('2')]:
			presenter.setFrameToBars("Browser")
			raise NextScene("Browser")
		elif event.key_code in [ord('3')]:
			presenter.setFrameToBars("Playlists")
			raise NextScene("Playlists")
		elif event.key_code in [ord('4')]:
			presenter.setFrameToBars("Medialib")
			raise NextScene("Medialib")
		elif event.key_code in [ord('5')]:
			presenter.setFrameToBars("Visualizer")
			raise NextScene("Visualizer")
		elif event.key_code in [ord('6')]:
			presenter.setFrameToBars("Equalizer")
			raise NextScene("Equalizer")
		elif event.key_code in [ord('7')]:
			presenter.artistinfoUpdateText()
			presenter.setFrameToBars("ArtistInfo")
			raise NextScene("ArtistInfo")
		elif event.key_code in [ord('8')]:
			presenter.lyricsUpdateText()
			presenter.setFrameToBars("Lyrics")
			raise NextScene("Lyrics")
		elif event.key_code in [ord('0')]:
			presenter.setFrameToBars("Clock")
			raise NextScene("Clock")
		elif event.key_code in [ord('9')]:
			presenter.setFrameToBars("Search")
			raise NextScene("Search")

class VisualParam(Enum):
	WAVE = 1
	SPECTRUM = 2
	LORENZ = 3
	KASSINI = 4
	CIRCLE = 5
	ELLIPSE = 6
	SIN_SPIRAL = 7
	LOG_SPIRAL = 8
	FERMA_SPIRAL = 9
	KORNU_SPIRAL = 10
	ARHIMED_SPIRAL = 11
	EPITROHOIDA = 12
	GIPOTROHOIDA = 13
	SQUARE = 14
	TEST = -1
strToVisualParam = {
	'wave': VisualParam.WAVE,
	'spectrum': VisualParam.SPECTRUM,
	'lorenz': VisualParam.LORENZ,
	'kassini': VisualParam.KASSINI,
	'circle': VisualParam.CIRCLE,
	'ellipse': VisualParam.ELLIPSE,
	'sin_spiral': VisualParam.SIN_SPIRAL,
	'log_spiral': VisualParam.LOG_SPIRAL,
	'ferma_spiral': VisualParam.FERMA_SPIRAL,
	'kornu_spiral': VisualParam.KORNU_SPIRAL,
	'arhimed_spiral': VisualParam.ARHIMED_SPIRAL,
	'epitrohoida': VisualParam.EPITROHOIDA,
	'gipotrohoida': VisualParam.GIPOTROHOIDA,
	'square': VisualParam.SQUARE,
}
	
class CustomVisualizer(Effect):
	def __init__(self, screen, config, upBarSize, downBarSize, color,
		bg=0, **kwargs):
		super(CustomVisualizer, self).__init__(screen, **kwargs)

		self.param = []
		params = config.visualization.visualization_types.split(":")
		cdict = config.visualization._asdict()
		for key in params:
			self.param.append(cdict[key])
	
		self.vParam = None
		self.vParamId = 0
		if self.param != []:
			self.vParam = strToVisualParam[self.param[0].type]

		self.bg = bg

		self.channel = 0
		self.spectbuf = []

		self._speed = 1

		self.upBarSize = upBarSize
		self.downBarSize = downBarSize

		self.k_max_rotation_count = 1000.0
		self.m_rotation_count_left = 0.0
		self.m_rotation_count_right = 0.0
		self._frame_no = 0

	def reset(self):
		pass
	def setPresenter(self, presenter):
		self.presenter = presenter
	
	_16_palette = [1, 1, 3, 3, 2, 2, 6, 6, 4, 4, 5, 5]
	_8_palette = [0, 1, 2, 3, 4, 5, 6, 7, 8]

	def rainbow(self, x, y):
		return self._16_palette[(x + y) % len(self._16_palette)]
	def rainbowHorizontal(self, x, y):
		step = int(self._screen.width / 6)
		res = x // step + 1
		return self._8_palette[res]
	def rainbowVertical(self, x, y):
		step = int(self._screen.height / 6)
		res = y // step + 1
		return self._8_palette[res]
	def rainbowCircle(self, r, R=None):
		if R == None:
			R = self._screen.width if self._screen.width > self._screen.height else self._screen.height
		step = int(R / 6)
		res = int(r) // step + 1
		if res >= 8:
			res = 7
		return self._8_palette[res]
	def rainbowP(self, x, y):
		step = int(self._screen.height / 6)
		res = y // step + 1
		return self._8_palette[len(self._8_palette)-res-2]

	def progressColor(self, i):
		_len = self.presenter.playerGetLen()
		_buf = self.presenter.playerGetBuf()
		pos = _buf*self._screen.width/_len
		if (i < pos):
			return 0
		return 1

	def updateWave(self, param):
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]
		#param
		isStereo = True if self.channel > 1 else False
		offset = 0
		if isStereo:
			self.spectrumHeight -= 10
			offset = -5
		#clear
		if self.spectbuf != []:
			for x, y in enumerate(self.spectbuf[0]):
				self._screen.print_at(' ', x,int(y)-offset,bg=0)
			if isStereo:
				for x, y in enumerate(self.spectbuf[1]):
					self._screen.print_at(' ', x,int(y)-offset-5,bg=0)
		
		self.spectbuf = [[],[]]
		for c in range(0, self.channel):
			for x in range(0, self._screen.width):
				#val
				y = (1 - self.buf[x * self.channel + c]) * self.spectrumHeight / 2
				if y < 0:
					y = 0
				elif y >= self.spectrumHeight:
					y = self.spectrumHeight - 1
				#color
				color = None
				if param.color.split(":")[0] == "progress":
					colorsList = param.color.split(":")
					prParam = self.progressColor(x)
					if prParam:
						color = ColorTheme(getColor(colorsList[1]), getAttr(colorsList[2]), getColor(colorsList[3]))
					else:
						color = ColorTheme(getColor(colorsList[4]), getAttr(colorsList[5]), getColor(colorsList[6]))
				elif param.color == "rainbow":
					color = ColorTheme(self.rainbow(x, int(y)), 2, self.bg)
				elif param.color == "rainbow_h":
					color = ColorTheme(self.rainbowHorizontal(x, int(y)), 2, self.bg)
				elif param.color == "rainbow_v":
					color = ColorTheme(self.rainbowVertical(x, int(y)), 2, self.bg)
				elif param.color == "rainbow_p":
					color = ColorTheme(self.rainbowP(x, int(y)), 2, self.bg)
				elif param.color == "rainbow_c":
					color = ColorTheme(self.rainbowCircle(x), 2, self.bg)######
				else:
					colorsList = param.color.split(":")
					color = ColorTheme(getColor(colorsList[0]), getAttr(colorsList[1]), getColor(colorsList[2]))
				#print
				if c == 0:
					self._screen.print_at(param.symbol, x,int(y)-offset,colour=color.color, attr=color.attr, bg=color.bg)
					self.spectbuf[0].append(y)
				else:
					self._screen.print_at(param.symbol, x,int(y)-5-offset,colour=color.color, attr=color.attr, bg=color.bg)
					self.spectbuf[1].append(y)
			if c == 1:
				break

	def updateSquare(self, param):
		oldBuf = self.spectbuf
		
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		startY = (self._screen.height - self.downBarSize - self.upBarSize) // 2 + self.upBarSize

		startX = self._screen.width // 2

		self.spectbuf = [[],[]]
		isStereo = True if self.channel > 1 else False
		
		self.spectrumHeight = (self._screen.height-self.downBarSize-self.upBarSize)

		for x in range(0, self._screen.width):
			if x >= 1022:
				break
			#v = 0 if self.buf[x + 1] < 0 else self.buf[x + 1]
			#y = sqrt(v) * 5 * self.spectrumHeight - 4
			y = self.buf[x + 1] * self.spectrumHeight
			if y > self.spectrumHeight:
				y = self.spectrumHeight
			self.spectbuf[0].append(int(y))
			if isStereo:
				self.spectbuf[1].append(int(y))

		squareSize = param.squareSize

		def _getColor(x, y):
			if param.color == "rainbow":
				color = ColorTheme(self.rainbow(int(x), int(y)), 2, self.bg)
			elif param.color == "rainbow_h":
				color = ColorTheme(self.rainbowHorizontal(int(x), int(y)), 2, self.bg)
			elif param.color == "rainbow_v":
				color = ColorTheme(self.rainbowVertical(int(x), int(y)), 2, self.bg)
			elif param.color == "rainbow_p":
				color = ColorTheme(self.rainbowP(int(x), int(y)), 2, self.bg)
			elif param.color == "rainbow_c":
				color = ColorTheme(self.rainbowCircle(x), 2, self.bg)#
			else:
				color = ColorTheme(getColor(colorsList[0]), getAttr(colorsList[1]), getColor(colorsList[2]))
			return color

		
		def ptintPart(ch, rstart, rend, start, needColor=True, swapXY=False, plusOrMinus=1):
			for ii in range(rstart, rend):
				end = []
				if needColor:
					end = self.spectbuf[0][self.__ii]
				else:
					end = oldBuf[0][self.__ii]
				j = 0
				while (j < end and j < self.spectrumHeight // 2):
					x = ii
					y = start - j*plusOrMinus
					if swapXY:
						x,y=y,x
					if needColor:
						color = None
						if param.color == "rainbow_c":
							r = 0
							if swapXY:
								r = sqrt(abs(y-abs(rstart-rend)) ** 2 + abs(x-start) ** 2)
							else:
								r = sqrt(abs(y-start) ** 2 + abs(x-abs(rstart-rend)) ** 2)
							color = _getColor(r, y)
						else:
							color = _getColor(x, y)
						self._screen.print_at(param.symbol, x, y, colour=color.color, attr=color.attr, bg=color.bg)
					else:
						self._screen.print_at(ch, x, y, bg=self.bg)
					j+=1
				self.__ii+=1

		#clear
		self.__ii = 0
		colorsList = param.color.split(":")
		if oldBuf != [] and oldBuf[0] != []:
			if not isStereo:
				ptintPart(' ', startX-squareSize//2, startX+squareSize//2, self.spectrumHeight // 2 + self.upBarSize, False, False, 1)
				ptintPart(' ', startX-squareSize//2, startX+squareSize//2, self.spectrumHeight // 2 + self.upBarSize, False, False, -1)
				ptintPart(' ', startY-squareSize//2, startY+squareSize//2, self._screen.width // 2, False, True, 1)
				ptintPart(' ', startY-squareSize//2, startY+squareSize//2, self._screen.width // 2, False, True, -1)
			else:
				ptintPart(' ', startX-squareSize//2-self._screen.width // 4, startX+squareSize//2-self._screen.width // 4, 
					self.spectrumHeight // 2 + self.upBarSize, False, False, 1)
				ptintPart(' ', startX-squareSize//2+self._screen.width // 4, startX+squareSize//2+self._screen.width // 4, 
					self.spectrumHeight // 2 + self.upBarSize, False, False, 1)
				ptintPart(' ', startX-squareSize//2-self._screen.width // 4, startX+squareSize//2-self._screen.width // 4, 
					self.spectrumHeight // 2 + self.upBarSize, False, False, -1)
				ptintPart(' ', startX-squareSize//2+self._screen.width // 4, startX+squareSize//2+self._screen.width // 4, 
					self.spectrumHeight // 2 + self.upBarSize, False, False, -1)
				
				ptintPart(' ', startY-squareSize//2, startY+squareSize//2, self._screen.width // 4, False, True, 1)
				ptintPart(' ', startY-squareSize//2, startY+squareSize//2, (self._screen.width // 4)*3, False, True, 1)
				ptintPart(' ', startY-squareSize//2, startY+squareSize//2, self._screen.width // 4, False, True, -1)
				ptintPart(' ', startY-squareSize//2, startY+squareSize//2, (self._screen.width // 4)*3, False, True, -1)
		
		self.__ii = 0
		if not isStereo:
			ptintPart(param.symbol, startX-squareSize//2, startX+squareSize//2, self.spectrumHeight // 2 + self.upBarSize, True, False, 1)
			ptintPart(param.symbol, startX-squareSize//2, startX+squareSize//2, self.spectrumHeight // 2 + self.upBarSize, True, False, -1)
			ptintPart(param.symbol, startY-squareSize//2, startY+squareSize//2, self._screen.width // 2, True, True, 1)
			ptintPart(param.symbol, startY-squareSize//2, startY+squareSize//2, self._screen.width // 2, True, True, -1)
		else:
			ptintPart(param.symbol, startX-squareSize//2-self._screen.width // 4, startX+squareSize//2-self._screen.width // 4, 
				self.spectrumHeight // 2 + self.upBarSize, True, False, 1)
			ptintPart(param.symbol, startX-squareSize//2+self._screen.width // 4, startX+squareSize//2+self._screen.width // 4, 
				self.spectrumHeight // 2 + self.upBarSize, True, False, 1)
			ptintPart(param.symbol, startX-squareSize//2-self._screen.width // 4, startX+squareSize//2-self._screen.width // 4, 
				self.spectrumHeight // 2 + self.upBarSize, True, False, -1)
			ptintPart(param.symbol, startX-squareSize//2+self._screen.width // 4, startX+squareSize//2+self._screen.width // 4, 
				self.spectrumHeight // 2 + self.upBarSize, True, False, -1)
			
			ptintPart(param.symbol, startY-squareSize//2, startY+squareSize//2, self._screen.width // 4, True, True, 1)
			ptintPart(param.symbol, startY-squareSize//2, startY+squareSize//2, (self._screen.width // 4)*3, True, True, 1)
			ptintPart(param.symbol, startY-squareSize//2, startY+squareSize//2, self._screen.width // 4, True, True, -1)
			ptintPart(param.symbol, startY-squareSize//2, startY+squareSize//2, (self._screen.width // 4)*3, True, True, -1)
		
	def updateSpectrum(self, param):
		oldBuf = self.spectbuf
		
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]
		start = self._screen.height - self.downBarSize - 1
		
		self.spectbuf = [[],[]]
		isStereo = True if self.channel > 1 else False
		if isStereo:
			start = start // 2
			self.spectrumHeight //= 3
		
		for x in range(0, self._screen.width):
			if x >= 1022:
				break
			
			#v = 0 if self.buf[x + 1] < 0 else self.buf[x + 1]
			#y = sqrt(v) * 5 * self.spectrumHeight - 4
			y = self.buf[x + 1] * 2 * self.spectrumHeight
			if y > self.spectrumHeight:
				y = self.spectrumHeight
			self.spectbuf[0].append(int(y))
			if isStereo:
				self.spectbuf[1].append(int(y))
		i = 0
		for ii in range(0, self._screen.width, 3):
			if oldBuf != [] and oldBuf[0] != []:
				if oldBuf[0][i] < self.spectbuf[0][i]:
					end = self.spectbuf[0][i]
					j = 0 if oldBuf[0][i] < 0 else oldBuf[0][i]
					while (j < end):
						color = None
						if param.color.split(":")[0] == "progress":
							colorsList = param.color.split(":")
							prParam = self.progressColor(ii)
							if prParam:
								color = ColorTheme(getColor(colorsList[1]), getAttr(colorsList[2]), getColor(colorsList[3]))
							else:
								color = ColorTheme(getColor(colorsList[4]), getAttr(colorsList[5]), getColor(colorsList[6]))
						elif param.color == "rainbow":
							color = ColorTheme(self.rainbow(ii, int(start - j)), 2, self.bg)
						elif param.color == "rainbow_h":
							color = ColorTheme(self.rainbowHorizontal(ii, int(start - j)), 2, self.bg)
						elif param.color == "rainbow_v":
							color = ColorTheme(self.rainbowVertical(ii, int(start - j)), 2, self.bg)
						elif param.color == "rainbow_p":
							color = ColorTheme(self.rainbowP(ii, int(end)), 2, self.bg)
						elif param.color == "rainbow_c":
							color = ColorTheme(self.rainbowCircle(ii), 2, self.bg)######
						else:
							colorsList = param.color.split(":")
							color = ColorTheme(getColor(colorsList[0]), getAttr(colorsList[1]), getColor(colorsList[2]))
						self._screen.print_at(param.symbol, ii, start - j, colour=color.color, attr=color.attr, bg=color.bg)
						if isStereo:
							self._screen.print_at(param.symbol, ii, start + j,colour=color.color, attr=color.attr, bg=color.bg)
						j+=1
				else:
					if oldBuf[0][i] > self.spectbuf[0][i]:
						end = oldBuf[0][i]
						j = 0 if self.spectbuf[0][i] < 0 else self.spectbuf[0][i]
						while (j < end):
							self._screen.print_at(' ', ii, start - j, bg=self.bg)
							if isStereo:
								self._screen.print_at(' ', ii, start + j, bg=self.bg)
							j+=1
			else:
				j = 0
				while (j < self.spectbuf[0][i]):
					color = None
					if param.color.split(":")[0] == "progress":
						colorsList = param.color.split(":")
						prParam = self.progressColor(ii)
						if prParam:
							color = ColorTheme(getColor(colorsList[1]), getAttr(colorsList[2]), getColor(colorsList[3]))
						else:
							color = ColorTheme(getColor(colorsList[4]), getAttr(colorsList[5]), getColor(colorsList[6]))
					elif param.color == "rainbow":
						color = ColorTheme(self.rainbow(ii, int(start - j)), 2, self.bg)
					elif param.color == "rainbow_h":
						color = ColorTheme(self.rainbowHorizontal(ii, int(start - j)), 2, self.bg)
					elif param.color == "rainbow_v":
						color = ColorTheme(self.rainbowVertical(ii, int(start - j)), 2, self.bg)
					elif param.color == "rainbow_p":
						color = ColorTheme(self.rainbowP(ii, int(self.spectbuf[0][i])), 2, self.bg)
					elif param.color == "rainbow_c":
						color = ColorTheme(self.rainbowCircle(ii), 2, self.bg)######
					else:
						colorsList = param.color.split(":")
						color = ColorTheme(getColor(colorsList[0]), getAttr(colorsList[1]), getColor(colorsList[2]))
					self._screen.print_at(param.symbol, ii, start - j, colour=color.color, attr=color.attr, bg=color.bg)
					if isStereo:
						self._screen.print_at(param.symbol, ii, start + j, colour=color.color, attr=color.attr, bg=color.bg)
					j+=1
			i+=1

	def updateLorenz(self, param):
			k_lorenz_h = 0.01
			k_lorenz_a = 10.0
			k_lorenz_b1 = 7.1429
			k_lorenz_b2 = 0.000908845
			k_lorenz_c = 8.0 / 3.0

			oldBuf = self.spectbuf
			for p in oldBuf:
				self._screen.print_at(' ', p[0], p[1], bg=self.bg)
			
			self.spectbuf = []
			data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
			if data == None:
				return
			self.channel = data["channel"]
			self.buf = data["data"]

			win_height = self.effectSize
			half_height = win_height / 2
			win_width = self.screen.width

			self.m_rotation_count_left = 0 if self.m_rotation_count_left >= \
				self.k_max_rotation_count else self.m_rotation_count_left
			self.m_rotation_count_right = 0 if self.m_rotation_count_right >= \
				self.k_max_rotation_count else self.m_rotation_count_right

			average_left = 0.0
			average_right = 0.0
			to = 500 if len(self.buf) > 500 else len(self.buf)
			for i in range(0, to, 2):
				average_left += abs(self.buf[i]) * 10
				average_right += abs(self.buf[i+1]) * 10

			average_left = average_left / 500 * 2.0 * 50
			average_right = average_right / 500 * 50

			rotation_interval_left =\
				(average_left * (10000 / 65536.0)) * 10
			rotation_interval_right =\
				(average_right * (10000 / 65536.0)) * 10

			overridden_scaling_multiplier = 1000
			average = overridden_scaling_multiplier * (average_left + average_right) / 2.0
		
			lorenz_b = k_lorenz_b1 + k_lorenz_b2 * average

			z_center = -1 + lorenz_b
			equilbria = sqrt(k_lorenz_c * lorenz_b - k_lorenz_c)

			scaling_multiplier =\
				1.25 * (half_height) /\
				sqrt((k_lorenz_c * lorenz_b * lorenz_b) -\
						(pow(z_center - lorenz_b, 2) / pow(lorenz_b, 2)))

			k_pi = 3.14159265358979323846
			rotation_angle_x = (self.m_rotation_count_left * 2.0 * k_pi) /\
									self.k_max_rotation_count
			rotation_angle_y =\
				(self.m_rotation_count_right * 2.0 * k_pi) /\
				self.k_max_rotation_count

			deg_multiplier_cos_x = cos(rotation_angle_x)
			deg_multiplier_sin_x = sin(rotation_angle_x)

			deg_multiplier_cos_y = cos(rotation_angle_y)
			deg_multiplier_sin_y = sin(rotation_angle_y)

			x = 0.0
			y = 0.0
			z = 0.0

			x0 = 0.1
			y0 = 0.0
			z0 = 0.0

			for i in range(0, 500):
				x1 = x0 + k_lorenz_h * k_lorenz_a * (y0 - x0)
				y1 = y0 + k_lorenz_h * (x0 * (lorenz_b - z0) - y0)
				z1 = z0 + k_lorenz_h * (x0 * y0 - k_lorenz_c * z0)
				x0 = x1
				y0 = y1
				z0 = z1
				# We want to rotate around the center of the lorenz. so we offset zaxis
				# so that the center of the lorenz is at point (0,0,0)
				x = x0
				y = y0
				z = z0 - z_center

				# Rotate around X and Y axis.
				xRxy = x * deg_multiplier_cos_y + z * deg_multiplier_sin_y
				yRxy = x * deg_multiplier_sin_x * deg_multiplier_sin_y +\
							y * deg_multiplier_cos_x -\
							z * deg_multiplier_cos_y * deg_multiplier_sin_x

				x = xRxy * scaling_multiplier
				y = yRxy * scaling_multiplier

				# Throw out any points outside the window
				if (y > (half_height * -1) and y < half_height and \
					x > (win_width / 2.0) * -1 and \
					x < (win_width / 2.0)):
					# skip the first 100 since values under 100 stick out too much from
					# the reset of the points
					if (i > 100):

						color = None
						if param.color.split(":")[0] == "progress":
							colorsList = param.color.split(":")
							color = ColorTheme(getColor(colorsList[1]), getAttr(colorsList[2]), getColor(colorsList[3]))
						elif param.color == "rainbow":
							color = ColorTheme(self.rainbow((int)(x + win_width / 2.0), 
								(int)(y + half_height)), 2, self.bg)
						elif param.color == "rainbow_h":
							color = ColorTheme(self.rainbowHorizontal((int)(x + win_width / 2.0), 
								(int)(y + half_height)), 2, self.bg)
						elif param.color == "rainbow_v":
							color = ColorTheme(self.rainbowVertical((int)(x + win_width / 2.0), 
								(int)(y + half_height)), 2, self.bg)
						elif param.color == "rainbow_p":
							color = ColorTheme(self.rainbowP((int)(x + win_width / 2.0), 
								(int)(y + half_height)), 2, self.bg)
						elif param.color == "rainbow_c":
							color = ColorTheme(self.rainbowCircle((int)(x + win_width / 2.0)), 2, self.bg)######
						else:
							colorsList = param.color.split(":")
							color = ColorTheme(getColor(colorsList[0]), getAttr(colorsList[1]), getColor(colorsList[2]))
						self.spectbuf.append(((int)(x + win_width / 2.0), 
							(int)(y + half_height)))
						self._screen.print_at(param.symbol, (int)(x + win_width / 2.0), 
							(int)(y + half_height),
							colour=color.color, attr=color.attr, bg=color.bg)
					
			self.m_rotation_count_left += rotation_interval_left
			self.m_rotation_count_right += rotation_interval_right


	def updateKassini(self, param):
		oldBuf = self.spectbuf
		
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width if not param.is_stereo else self._screen.width // 2
		
		#clear
		for p in oldBuf:
			self._screen.print_at(' ', p[0], p[1], bg=self.bg)

		#kassini
		def y(x, a, c):
			v = sqrt(a**4+4*c*c*x*x) - x*x - c*c
			if v < 0:
				return -1
			else:
				return (int)(sqrt( sqrt(a**4+4*c*c*x*x) - x*x - c*c ))
		a1arr=[]
		a2arr=[]
		n1 = 0.0
		n2 = 0.0
		step = 2 if param.is_stereo else 1
		go = 0
		vizSize = 5
		c = (w // 3) // 2
		for j in range(vizSize):
			for i in range(go, go+30, step):
				n1 += abs(self.buf[i])
				if param.is_stereo:
					n2 += abs(self.buf[i+1])
			a1 = n1*c
			a2 = n2*c
			a1arr.append(a1)
			a2arr.append(a2)
			go+=30
		self.spectbuf = []
		for j in range(vizSize):
			for x in range(0, w):
				_y = y(x - w//2, a1arr[j], c)
				if _y < 0 or _y+h//2 < start or _y+h//2 > end or -_y+h//2 < start or -_y+h//2 > end:
					continue
				self.spectbuf.append((x, _y+h//2, a1arr[j]))
				self.spectbuf.append((x, -_y+h//2, a1arr[j]))
				if param.is_stereo:
					_y = y(x - w//2, a2arr[j], c)
					if _y < 0 or _y+h//2 < start or _y+h//2 > end or -_y+h//2 < start or -_y+h//2 > end:
						continue
					self.spectbuf.append((x+w, _y+h//2, a2arr[j]))
					self.spectbuf.append((x+w, -_y+h//2, a2arr[j]))

		#print
		for p in self.spectbuf:
			if param.color == "rainbow_c":
				color = self.updateColor(param, p[2], None)####
			else:
				color = self.updateColor(param, p[0], p[1])
			self._screen.print_at(param.symbol, p[0], p[1],
				colour=color.color, attr=color.attr, bg=color.bg)

	def updateCircle(self, param):
		oldBuf = self.spectbuf
		
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width if not param.is_stereo else self._screen.width // 2
		
		#clear
		for i, r in enumerate(self.spectbuf):
			for alpha in range(0, 360, 2):
				x = (int)(r * sin(alpha))
				y = (int)(r * cos(alpha))
				if param.color == "rainbow_c":
					color = self.updateColor(param, r, w//2)####
				else:
					color = self.updateColor(param, x+w//2, y+h//2)
				offset = 0
				if param.is_stereo:
					offset = 0 if i%2==0 else w
				if y+h//2 < start or y+h//2 > end:
					continue
				self._screen.print_at(' ', x+w//2+offset, y+h//2,
					bg=self.bg)

		#circle
		step = 2 if param.is_stereo else 1
		vizSize = 10 if param.is_stereo else 5
		scale = 2 if param.is_stereo else 3
		self.spectbuf = []
		for i in range(0, vizSize, step):
			r = abs(self.buf[i]) * scale * w
			if r > w//2:
				r = w//2
			self.spectbuf.append(r) #R
			if param.is_stereo:
				r = abs(self.buf[i+1])* scale * w
				if r > w//2:
					r = w//2
				self.spectbuf.append(r) #R

		#print
		for i, r in enumerate(self.spectbuf):
			for alpha in range(0, 360, 2):
				x = (int)(r * sin(alpha))
				y = (int)(r * cos(alpha))
				if param.color == "rainbow_c":
					color = self.updateColor(param, r, w//2)####
				else:
					color = self.updateColor(param, x+w//2, y+h//2)
				offset = 0
				if param.is_stereo:
					offset = 0 if i%2==0 else w
				if y+h//2 < start or y+h//2 > end:
					continue
				self._screen.print_at(param.symbol, x+w//2+offset, y+h//2,
					colour=color.color, attr=color.attr, bg=color.bg)

	def updateEllipse(self, param):
		oldBuf = self.spectbuf
		
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width
		
		vizSize = 1000 if len(self.buf) > 1000 else len(self.buf)
		#clear
		deg_multiplier = 2*3.1415/(vizSize)
		for i, r in enumerate(self.spectbuf):
			offset0 = 0
			offset1 = 0
			if param.is_stereo:
				offset0 = 0 if i % 2 == 0 else 3.1415/2
				offset1 = 3.1415/2*3 if i % 2 == 0 else 3.1415
			x = w / 2 * cos(i*deg_multiplier + offset0)
			y = h / 2 * sin(i*deg_multiplier + offset0)

			x *= self.spectbuf[i] / 15
			y *= self.spectbuf[i] / 15

			if y+h//2 < start or y+h//2 > end:
				continue
			self._screen.print_at(' ', (int)(x)+w // 2 , (int)(y)+h // 2, bg=self.bg)

			x = w / 2 * cos(i*deg_multiplier + offset1)
			y = h / 2 * sin(i*deg_multiplier + offset1)

			x *= self.spectbuf[i] / 15
			y *= self.spectbuf[i] / 15

			if y+h//2 < start or y+h//2 > end:
				continue
			self._screen.print_at(' ', (int)(x)+w // 2 , (int)(y)+h // 2, bg=self.bg)
		#ellipse
		step = 2 if param.is_stereo else 1
		
		self.spectbuf = []
		for i in range(0, vizSize, step):
			radius = abs(self.buf[i]*128.0) / 5.0
			self.spectbuf.append(radius) #R
			if param.is_stereo:
				radius = abs(self.buf[i+1]*128.0) / 5.0
				self.spectbuf.append(radius) #R

		#print
		deg_multiplier = 2*3.1415/(vizSize)
		for i, r in enumerate(self.spectbuf):
			offset0 = 0
			offset1 = 0
			if param.is_stereo:
				offset0 = 0 if i % 2 == 0 else 3.1415/2
				offset1 = 3.1415/2*3 if i % 2 == 0 else 3.1415
			x = w / 2 * cos(i*deg_multiplier + offset0)
			y = h / 2 * sin(i*deg_multiplier + offset0)
			max_radius = sqrt(x*x + y*y)

			x = x*(self.spectbuf[i]) / 15
			y = y*(self.spectbuf[i]) / 15

			radius = sqrt(x*x + y*y)
			if param.color == "rainbow_c":
				color = self.updateColor(param, r, w//2)####
			else:
				color = self.updateColor(param, (int)(x+w//2), (int)(y+h//2))
			if y+h//2 < start or y+h//2 > end:
				continue
			self._screen.print_at(param.symbol, (int)(x)+w // 2 , (int)(y)+h // 2,
				colour=color.color, attr=color.attr, bg=color.bg)

			x = w / 2 * cos(i*deg_multiplier + offset1)
			y = h / 2 * sin(i*deg_multiplier + offset1)

			x *= self.spectbuf[i] / 15
			y *= self.spectbuf[i] / 15

			if y+h//2 < start or y+h//2 > end:
				continue
			self._screen.print_at(param.symbol, (int)(x)+w // 2 , (int)(y)+h // 2,
				colour=color.color, attr=color.attr, bg=color.bg)

	def updateColor(self, param, x, y):
		color = None
		if param.color == "rainbow":
			color = ColorTheme(self.rainbow(x, y), 2, self.bg)
		elif param.color == "rainbow_h":
			color = ColorTheme(self.rainbowHorizontal(x, y), 2, self.bg)
		elif param.color == "rainbow_v":
			color = ColorTheme(self.rainbowVertical(x, y), 2, self.bg)
		elif param.color == "rainbow_p":
			color = ColorTheme(self.rainbowP(x, y), 2, self.bg)
		elif param.color == "rainbow_c":
			color = ColorTheme(self.rainbowCircle(x, y), 2, self.bg)
		else:
			colorsList = param.color.split(":")
			color = ColorTheme(getColor(colorsList[0]), getAttr(colorsList[1]), getColor(colorsList[2]))
		return color

	def updateSpiral(self, param):
		#clear
		for p in self.spectbuf:
			self._screen.print_at(' ', p[0], p[1], bg=self.bg)
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width if not param.is_stereo else self._screen.width // 2

		go = 0
		vizSize = 2
		step = 1 if not param.is_stereo else 2
		_buf = 30 if not param.is_stereo else 60
		nArr = []
		self.spectbuf = []
		for i in range(vizSize):
			n1 = 0.0
			n2 = 0.0
			for i in range(go, go+_buf, step):
				#n += abs(self.buf[i]/2) # 1
				n1 += abs(self.buf[i]) # 2
				if param.is_stereo:
					n2 += abs(self.buf[i+1])
			nArr.append(n1)
			if n2 != 0:
				nArr.append(n2)
		for i in range(vizSize):
			for _fi in range(0, 500, 1):
				#fi = 3.1415*2/360*_fi
				fi = 360/500*_fi
				#1 синусоидальная спираль
				if param.type == "sin_spiral":
					if pow(2, nArr[i])*sin(nArr[i]*fi) >= 0:
						r = sqrt(pow(3.1415, nArr[i])*sin(nArr[i]*fi))
					else:
						continue
				#2 архимедова спираль
				if param.type == "arhimed_spiral":
					r = nArr[i]/(2*pi)*fi

				#3 Логарифмическая спираль
				if param.type == "log_spiral":
					b = 0.14
					tetta = fi/pi
					r = nArr[i] * exp(b*tetta)

				#5 Спираль Ферма
				if param.type == "ferma_spiral":
					r = sqrt(nArr[i]*nArr[i]*fi)

				x = r*cos(fi+2*3.1415/(vizSize))
				y = r*sin(fi+2*3.1415/(vizSize))
				offset = 0
				if param.is_stereo:
					offset = 0 if i%2==0 else w
				
				if (int)(y + h / 2) < start or (int)(y + h / 2) > end:
					continue
				self.spectbuf.append(((int)(x + w / 2.0)+offset, (int)(y + h / 2)))
				color = self.updateColor(param, (int)(x + w / 2.0)+offset, (int)(y + h / 2))
				
				self._screen.print_at(param.symbol, (int)(x + w / 2.0)+offset, 
					(int)(y + h / 2),
					colour=color.color, attr=color.attr, bg=color.bg)
	
	alphaKornu = 0
	def updateSpiralKornu(self, param):
		#clear
		for p in self.spectbuf:
			self._screen.print_at(' ', p[0], p[1], bg=self.bg)
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width

		go = 0
		vizSize = 5
		step = 1 if not param.is_stereo else 2
		_buf = 30 if not param.is_stereo else 60
		nArr = []
		for i in range(vizSize):
			n1 = 0.0
			n2 = 0.0
			for i in range(go, go+_buf, step):
				#n += abs(self.buf[i]/2) # 1
				n1 += abs(self.buf[i])/3 # 2
				if param.is_stereo:
					n2 += abs(self.buf[i+1])/3
			nArr.append(n1)
			if n2 != 0:
				nArr.append(n2)
		#4 спираль Корню 
		self.spectbuf = []
		for n in nArr:
			T = n
			N = 100
			scale = 15
			dx = 0
			dy = 0 
			t=0
			prevX = 0
			prevY = 0
			currentX = 0
			currentY = 0
			prevX2 = 0
			prevY2 = 0
			currentX2 = 0
			currentY2 = 0
			dt = T/N
			while N >= 0:
				dx = cos(t*t) * dt
				dy = sin(t*t) * dt
				t += dt
				currentX = prevX + dx
				currentY = prevY + dy
				currentX2 = prevX2 - dx
				currentY2 = prevY2 - dy
				_x = currentX*cos(pi) + currentY*sin(pi)
				_y = currentY*cos(pi) - currentX*sin(pi)
				__x = (int)(_x*scale * cos(self.alphaKornu) + w / 2.0)
				__y = (int)(_y*scale * sin(self.alphaKornu)  + h / 2.0)
				if __y < start or __y > end:
					pass
				else:
					self.spectbuf.append((__x, __y))
					color = self.updateColor(param, __x, __y)
					self._screen.print_at(param.symbol, __x, __y,
						colour=color.color, attr=color.attr, bg=color.bg)

				_x = currentX2*cos(pi) + currentY2*sin(pi)
				_y = currentY2*cos(pi) - currentX2*sin(pi)
				__x = (int)(_x*scale * cos(self.alphaKornu) + w / 2.0)
				__y = (int)(_y*scale * sin(self.alphaKornu) + h / 2.0)
				if __y < start or __y > end:
					pass
				else:
					self.spectbuf.append((__x, __y))
					color = self.updateColor(param, __x, __y)
					self._screen.print_at(param.symbol, __x, __y,
						colour=color.color, attr=color.attr, bg=color.bg)
				prevX = currentX
				prevY = currentY
				prevX2 = currentX2
				prevY2 = currentY2
				N -= 1
		self.alphaKornu += 0.02
		if self.alphaKornu > 6.3:
			self.alphaKornu = 0

	def updateEpitrohoida(self, param):
		#clear
		for p in self.spectbuf:
			self._screen.print_at(' ', p[0], p[1], bg=self.bg)
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width if not param.is_stereo else self._screen.width // 2

		go = 0
		vizSize = 1
		step = 1 if not param.is_stereo else 2
		_buf = 30 if not param.is_stereo else 60
		nArr = []
		for i in range(vizSize):
			n1 = 0.0
			n2 = 0.0
			for i in range(go, go+_buf, step):
				#n += abs(self.buf[i]/2) # 1
				n1 += abs(self.buf[i]) # 2
				if param.is_stereo:
					n2 += abs(self.buf[i+1])
			nArr.append(n1)
			if n2 != 0:
				nArr.append(n2)

		R = min(h, w) // 3 - 2
		# h= R+r - роза; h=r - Эпициклоида
		self.spectbuf = []
		for i, n in enumerate(nArr):
			for fi in range(0, 360, 2):
				#Эпитрохоида
				r = n
				m = r/R

				if param.h == "R+r" or param.h == "r+R":
					_h = R+r
				elif param.h == "R":
					_h = R
				elif param.h == "r":
					_h = r
				else:
					_h = float(param.h)

				x = R*(m+1)*cos(m*fi) - _h*cos((m+1)*fi)
				y = R*(m+1)*sin(m*fi) - _h*sin((m+1)*fi)
				
				offset = 0
				if param.is_stereo:
					offset = 0 if i%2==0 else w
				
				if (int)(y + h / 2) < start or (int)(y + h / 2) > end:
					continue
				self.spectbuf.append(((int)(x + w / 2.0)+offset, (int)(y + h / 2.0)))
				color = self.updateColor(param, (int)(x + w / 2.0)+offset, (int)(y + h / 2.0))
				
				self._screen.print_at(param.symbol, (int)(x + w / 2.0)+offset, 
					(int)(y + h / 2.0),
					colour=color.color, attr=color.attr, bg=color.bg)
	
	def updateGipotrohoida(self, param):
		#clear
		for p in self.spectbuf:
			self._screen.print_at(' ', p[0], p[1], bg=self.bg)
		#data
		data = self.presenter.playerGetWaveData(param.is_stereo, self._screen.width)
		if data == None:
			return
		self.channel = data["channel"]
		self.buf = data["data"]

		end = self._screen.height - self.downBarSize - 1
		start = self.upBarSize + 1
		h = end - start
		w = self._screen.width if not param.is_stereo else self._screen.width // 2

		go = 0
		vizSize = 1
		step = 1 if not param.is_stereo else 2
		_buf = 30 if not param.is_stereo else 60
		nArr = []
		for i in range(vizSize):
			n1 = 0.0
			n2 = 0.0
			for i in range(go, go+_buf, step):
				#n += abs(self.buf[i]/2) # 1
				n1 += abs(self.buf[i]) # 2
				if param.is_stereo:
					n2 += abs(self.buf[i+1])
			nArr.append(n1)
			if n2 != 0:
				nArr.append(n2)

		R = min(h, w) // 3 - 2
		# h= R+r - роза; h=r - Эпициклоида
		self.spectbuf = []
		for i, n in enumerate(nArr):
			for fi in range(0, 360, 2):
				#Эпитрохоида
				r = n

				if param.h == "R+r" or param.h == "r+R":
					_h = R+r
				elif param.h == "R":
					_h = R
				elif param.h == "r":
					_h = r
				else:
					_h = float(param.h)

				if r*fi == 0:
					continue

				x = (R-r)*cos(fi) - _h*cos((R-r)/r*fi)
				y = (R-r)*sin(fi) - _h*sin((R-r)/r*fi)
				
				offset = 0
				if param.is_stereo:
					offset = 0 if i%2==0 else w
				
				if (int)(y + h / 2) < start or (int)(y + h / 2) > end:
					continue
				self.spectbuf.append(((int)(x + w / 2.0)+offset, (int)(y + h / 2.0)))
				color = self.updateColor(param, (int)(x + w / 2.0)+offset, (int)(y + h / 2.0))
				
				self._screen.print_at(param.symbol, (int)(x + w / 2.0)+offset, 
					(int)(y + h / 2.0),
					colour=color.color, attr=color.attr, bg=color.bg)
	
	def next(self):
		if self.param != []:
			end = self._screen.height - self.downBarSize - 1
			start = self.upBarSize + 1
			for i in range(start, end+1):
				self._screen.print_at(' '*self._screen.width, 0, i, bg=self.bg)

			self.spectbuf = []
			self.vParamId = self.vParamId+1 if self.vParamId+1 < len(self.param) else 0
			self.vParam = strToVisualParam[self.param[self.vParamId].type]

	def _update(self, frame_no):
		self._frame_no = frame_no
		self.effectSize = self._screen.height - self.upBarSize - self.downBarSize
		self.spectrumHeight = 0 if self.effectSize <= 0 else self.effectSize

		if self.vParam == VisualParam.WAVE:
			self.updateWave(self.param[self.vParamId])
		if self.vParam == VisualParam.SPECTRUM:
			self.updateSpectrum(self.param[self.vParamId])
		if self.vParam == VisualParam.LORENZ:
			self.updateLorenz(self.param[self.vParamId])
		if self.vParam == VisualParam.KASSINI:
			self.updateKassini(self.param[self.vParamId])
		if self.vParam == VisualParam.CIRCLE:
			self.updateCircle(self.param[self.vParamId])
		if self.vParam == VisualParam.ELLIPSE:
			self.updateEllipse(self.param[self.vParamId])
		if self.vParam == VisualParam.KORNU_SPIRAL:
			self.updateSpiralKornu(self.param[self.vParamId])
		if self.vParam in [VisualParam.SIN_SPIRAL,
			VisualParam.ARHIMED_SPIRAL, VisualParam.FERMA_SPIRAL, VisualParam.LOG_SPIRAL]:
			self.updateSpiral(self.param[self.vParamId])
		if self.vParam == VisualParam.EPITROHOIDA:
			self.updateEpitrohoida(self.param[self.vParamId])
		if self.vParam == VisualParam.GIPOTROHOIDA:
			self.updateGipotrohoida(self.param[self.vParamId])
		if self.vParam == VisualParam.SQUARE:
			self.updateSquare(self.param[self.vParamId])
	@property
	def stop_frame(self):
		return self._stop_frame

	@property
	def frame_update_count(self):
		return self._speed - (self._frame_no % self._speed)

	def __clear(self):
		for i in range(0, len(self.spectbuf)):
			j = 0
			if self.spectbuf == []:
				break
			while (j < self.spectbuf[i]):
				start = 30
				self._screen.print_at(' ', i*3, start  - j,bg=0)
				j+=1


class CustomFigletText(Effect):
	ncmpcpp = {
		'zero': [
		'###### ',
		'#    # ',
		'#    # ',
		'#    # ',
		'###### '],
		'one': [
		'     # ',
		'     # ',
		'     # ',
		'     # ',
		'     # '],
		'two':  [
		'###### ',
		'     # ',
		'###### ',
		'#      ',
		'###### '],
		'three': [
		'###### ',
		'     # ',
		'###### ',
		'     # ',
		'###### '],
		'four': [
		'#    # ',
		'#    # ',
		'###### ',
		'     # ',
		'     # '],
		'five': [
		'###### ',
		'#      ',
		'###### ',
		'     # ',
		'###### '],
		'six': [
		'###### ',
		'#      ',
		'###### ',
		'#    # ',
		'###### '],
		'seven': [
		'###### ',
		'     # ',
		'     # ',
		'     # ',
		'     # '],
		'eight': [
		'###### ',
		'#    # ',
		'###### ',
		'#    # ',
		'###### '],
		'nine': [
		'###### ',
		'#    # ',
		'###### ',
		'     # ',
		'###### '],
		'dot': [
		'   ',
		' # ',
		'   ',
		' # ',
		'   ']
	}

	def __init__(self, screen, dup, ddown, needSec, font=DEFAULT_FONT, config=None, width=200, **kwargs):
		super(CustomFigletText, self).__init__(screen, **kwargs)
		self.w = self._screen.width
		self.h = self._screen.height - dup - ddown
		self.xStart = 0
		self.yStart = dup
		self.border = config.clock.border
		self.colorWall = getColor(config.bg_color)
		self.type = config.clock.type
		#analog
		if self.type == "analog":
			c = config.clock.analog.centr_color.split(':')
			self.colorC  = c[0] if c[0]=="rainbow" else ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			c = config.clock.analog.hour_color.split(':')
			self.colorH  = c[0] if c[0]=="rainbow" else ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			c = config.clock.analog.minutes_color.split(':')
			self.colorM  = c[0] if c[0]=="rainbow" else ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			c = config.clock.analog.seconds_color.split(':')
			self.colorS  = c[0] if c[0]=="rainbow" else ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			if self.colorC == "rainbow" or\
				self.colorH == "rainbow" or\
				self.colorM == "rainbow" or\
				self.colorS == "rainbow":
				self.colorC = self.colorH = self.colorM = self.colorS = "rainbow"
			self.radius = min(self.w, self.h) // 2 - 4
		if self.type == "binary":
			c = config.clock.binary.active_color.split(':')
			self.colorA  = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			c = config.clock.binary.hide_color.split(':')
			self.colorH  = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		if self.type == "digital":
			c = config.clock.digital.color.split(':')
			self.colorDg = c[0] if c[0]=="rainbow" else ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
			
			

		self.dup = dup
		self.ddown = ddown

		self.font = font
		self.needSeconds = needSec
		self.needCalendar = config.clock.need_calendar
		self.needBorder = config.clock.need_border
		
	def getCh(self, ch):
		return {
			'0': self.ncmpcpp['zero'],
			'1': self.ncmpcpp['one'],
			'2': self.ncmpcpp['two'],
			'3': self.ncmpcpp['three'],
			'4': self.ncmpcpp['four'],
			'5': self.ncmpcpp['five'],
			'6': self.ncmpcpp['six'],
			'7': self.ncmpcpp['seven'],
			'8': self.ncmpcpp['eight'],
			'9': self.ncmpcpp['nine'],
			':': self.ncmpcpp['dot']
		}[ch]

	def reset(self):
		pass

	def _update(self, frame_no):
		if self.type == 'analog':
			self._updateAnalog()
		elif self.type == 'binary':
			self._updateBin()
		elif self.type == 'digital':
			self._updateDigit()

	_8_palette = [1, 3, 2, 6, 4, 5]

	def rainbow(self, x, y):
		return self._8_palette[(x + y) % len(self._8_palette)]

	def _updateBin(self):
		new_time = datetime.datetime.now().timetuple()
		now = datetime.datetime.now()
		dayInfo = now.strftime("%d : %b : %Y : %a") 
		h = int(new_time.tm_hour)
		m = int(new_time.tm_min)
		s = int(new_time.tm_sec)

		_hour = self.genBin(h, _type='h')
		_min = self.genBin(m, _type='m')
		_sec = []
		if self.needSeconds:
			_sec = self.genBin(s, _type='s')

		res = []
		for i, _ in enumerate(_hour):
			res.append(_hour[i]+self.dot[i]+_min[i]+((self.dot[i]+_sec[i]) if _sec != [] else ""))
		_w = len(res[0]) // 2
		_h = len(res) // 2
		for i, t in enumerate(res):
			for j, c in enumerate(t):
				if c == '#':
					self._screen.print_at(' ', j - _w + self.w // 2, i - _h + self.h//2, \
						colour=self.colorA.color, attr=self.colorA.attr, bg=self.colorA.color)
				elif c == '*':
					self._screen.print_at(' ', j - _w + self.w//2, i - _h + self.h//2, \
						colour=self.colorH.color, attr=self.colorH.attr, bg=self.colorH.color)
				else:
					self._screen.print_at(' ', j - _w + self.w//2, i - _h + self.h//2, bg=self.colorWall)
		
		if self.needCalendar:
			for i, c in enumerate(dayInfo):
				_color = self.rainbow(self.w // 2+self.xStart-len(dayInfo)//2+i, self.h // 2+self.yStart+len(res)//2) \
					if self.colorA == "rainbow" else self.colorA.color
				_attr = 2 if self.colorA == "rainbow" else self.colorA.attr
				_bg = self.colorWall if self.colorA == "rainbow" else self.colorA.bg
				self._screen.print_at(c, 
					self.w // 2+self.xStart-len(dayInfo)//2+i, self.h // 2+self.yStart+len(res)//2+1, 
					colour=_color, attr=_attr, bg=_bg)

		clockH = len(res)+2
		clockW = len(res[0])
		sy = - _h + self.h//2-1
		sx = - _w + self.w//2-1
		if self.needBorder:
			x0 = sx-2
			y0 = sy
			x1 = sx-2
			y1 = sy+clockH+1
			x2 = sx+clockW+2
			y2 = sy+clockH+1
			x3 = sx+clockW+2
			y3 = sy
			self.drawBorder(x0,y0,x1,y1,x2,y2,x3,y3, self.colorA)

	dot = [
	'      ',
	'      ',
	'  ##  ',
	'  ##  ',
	'      ',
	'      ',
	'      ',
	'  ##  ',
	'  ##  ',
	'      ',
	'      ']

	def genBin(self, num, _type='h'):
		n1 = num // 10
		n2 = num % 10
		bn1 = bin(n1)
		bn2 = bin(n2)
		if _type == 'h':
			bn1 = bn1[len(bn1)-2:]
		else:
			bn1 = bn1[len(bn1)-3:]
		bn2 = bn2[len(bn2)-4:]

		buf = [['.'] * 6 for i in range(11)]

		if _type != 'h':
			buf[3][0]='*'; buf[3][1]='*'; buf[4][0]='*'; buf[4][1]='*'
		buf[6][0]='*'; buf[6][1]='*'; buf[7][0]='*'; buf[7][1]='*'
		buf[9][0]='*'; buf[9][1]='*'; buf[10][0]='*'; buf[10][1]='*'

		buf[0][3]='*'; buf[0][4]='*'; buf[1][3]='*'; buf[1][4]='*'
		buf[3][3]='*'; buf[3][4]='*'; buf[4][3]='*'; buf[4][4]='*'
		buf[6][3]='*'; buf[6][4]='*'; buf[7][3]='*'; buf[7][4]='*'
		buf[9][3]='*'; buf[9][4]='*'; buf[10][3]='*'; buf[10][4]='*'

		pos = 9
		for i in reversed(bn1):
			if i == '1':
				buf[pos][0]='#'; buf[pos][1]='#'; buf[pos+1][0]='#'; buf[pos+1][1]='#'
			pos -= 3

		pos = 9
		for i in reversed(bn2):
			if i == '1':
				buf[pos][3]='#'; buf[pos][4]='#'; buf[pos+1][3]='#'; buf[pos+1][4]='#'
			pos -= 3
		_buf = []
		for i in buf:
			s=''
			for j in i:
				s+=j
			_buf.append(s)

		return _buf

	def _updateDigit(self):
		new_time = datetime.datetime.now().timetuple()
		now = datetime.datetime.now()
		dayInfo = now.strftime("%d : %b : %Y : %a") 
		h = int(new_time.tm_hour)
		m = int(new_time.tm_min)
		s = int(new_time.tm_sec)
		text = str(h)+':'+str(m)
		if self.needSeconds:
			text += ':'+str(s)
		if self.font == "ncmpcpp":
			time=['','','','','']
			for t in text:
				_ch = self.getCh(t)
				time[0] += _ch[0]
				time[1] += _ch[1]
				time[2] += _ch[2]
				time[3] += _ch[3]
				time[4] += _ch[4]
			self._images = [time[0]+'\n'+time[1]+'\n'+time[2]+'\n'+time[3]+'\n'+time[4]]
		else:
			text = text.replace(':', ' : ')
			self._images = [Figlet(font=self.font, width=self.w ).renderText(text)]
		tx = self._images[0].split('\n')
		_w = len(tx[0]) // 2
		_h = len(tx) // 2
		for i, t in enumerate(tx):
			if self.font == 'ncmpcpp':
				for j, c in enumerate(t):
					_color = self.rainbow(j - _w + self.w // 2, i - _h + self.h//2) if self.colorDg == "rainbow" else self.colorDg.color
					_attr = 2 if self.colorDg == "rainbow" else self.colorDg.attr
					_bg = self.colorWall if self.colorDg == "rainbow" else self.colorDg.bg
					if c == '#':
						self._screen.print_at(' ', j - _w + self.w // 2, i - _h + self.h//2, 
							colour=_color, attr=_attr, bg=_color)
					else:
						self._screen.print_at(' ', j - _w + self.w // 2, i - _h + self.h//2, 
							colour=_color, attr=_attr, bg=self.colorWall)
			else:
				_color = self.rainbow(0 - _w + self.w//2, i - _h + self.h//2) if self.colorDg == "rainbow" else self.colorDg.color
				_attr = 2 if self.colorDg == "rainbow" else self.colorDg.attr
				_bg = self.colorWall if self.colorDg == "rainbow" else self.colorDg.bg
				self._screen.print_at(t,
					0 - _w + self.w//2, i - _h + self.h//2,
					colour=_color, attr=_attr, bg=_bg)

		if self.needCalendar:
			for i, c in enumerate(dayInfo):
				_color = self.rainbow(self.w // 2+self.xStart-len(dayInfo)//2+i, self.h // 2+self.yStart+len(tx)//2) \
					if self.colorDg == "rainbow" else self.colorDg.color
				_attr = 2 if self.colorDg == "rainbow" else self.colorDg.attr
				_bg = self.colorWall if self.colorDg == "rainbow" else self.colorDg.bg
				self._screen.print_at(c, 
					self.w // 2+self.xStart-len(dayInfo)//2+i, self.h // 2+self.yStart+len(tx)//2, 
					colour=_color, attr=_attr, bg=_bg)

		clockH = len(tx)+1
		clockW = len(tx[0])
		sy = - _h + self.h//2-1
		sx = - _w + self.w//2-1
		if self.needBorder:
			x0 = sx-2
			y0 = sy
			x1 = sx-2
			y1 = sy+clockH+1
			x2 = sx+clockW+2
			y2 = sy+clockH+1
			x3 = sx+clockW+2
			y3 = sy
			self.drawBorder(x0,y0,x1,y1,x2,y2,x3,y3, self.colorDg)
	
	def _updateAnalog(self):
		if self.radius < 0:
			return
		def _hour_pos(t):
			return (t.tm_hour + t.tm_min / 60) * pi / 6

		def _min_pos(t):
			return t.tm_min * pi / 30

		def _sec_pos(t):
			return t.tm_sec * pi / 30

		new_time = datetime.datetime.now().timetuple()
		now = datetime.datetime.now()
		dayInfo = now.strftime("%d : %b : %Y : %a") 
		self._images = [[[' '] * self.h for i in range(self.w)]]

		self._x = self.w // 2
		self._y = self.h // 2
		self.draw(self._x + (self.radius * sin(_hour_pos(new_time))),
			self._y - (self.radius * cos(_hour_pos(new_time)) / 2), self.colorH, bg=0)
		self._x = self.w // 2
		self._y = self.h // 2
		self.draw(self._x + (self.radius * sin(_min_pos(new_time)) * 2),
			self._y - (self.radius * cos(_min_pos(new_time))), self.colorM, bg=0)
		if self.needSeconds:
			self._x = self.w // 2
			self._y = self.h // 2
			self.draw(self._x + (self.radius * sin(_sec_pos(new_time)) * 2),
				self._y - (self.radius * cos(_sec_pos(new_time))), self.colorS,
				bg=0, thin=True)
		self._images[0][self.w // 2][self.h // 2] = 'o'
		self._oldImage = self._images[0]
		
		_color = self.rainbow(self.w // 2, self.h // 2) if self.colorC == "rainbow" else self.colorC.color
		_attr = 2 if self.colorC == "rainbow" else self.colorC.attr
		_bg = self.colorWall if self.colorC == "rainbow" else self.colorC.bg
		self._screen.print_at(self._images[0][self.w // 2][self.h // 2], 
			self.w // 2+self.xStart, self.h // 2+self.yStart, 
			colour=_color, attr=_attr, bg=_bg)
		if self.needCalendar:
			for i, c in enumerate(dayInfo):
				_color = self.rainbow(self.w // 2+self.xStart-len(dayInfo)//2+i, self.h // 2+self.yStart + self.radius-1) \
					if self.colorC == "rainbow" else self.colorC.color
				_attr = 2 if self.colorC == "rainbow" else self.colorC.attr
				_bg = self.colorWall if self.colorC == "rainbow" else self.colorC.bg
				self._screen.print_at(c, 
					self.w // 2+self.xStart-len(dayInfo)//2+i, self.h // 2+self.yStart + self.radius-1, 
					colour=_color, attr=_attr, bg=_bg)
		if self.needBorder:
			x0 = self.w // 2+self.xStart-self.radius-8
			y0 = self.h // 2+self.yStart-self.radius-3
			x1 = self.w // 2+self.xStart-self.radius-8
			y1 = self.h // 2+self.yStart+self.radius+3
			x2 = self.w // 2+self.xStart+self.radius+8
			y2 = self.h // 2+self.yStart+self.radius+3
			x3 = self.w // 2+self.xStart+self.radius+8
			y3 = self.h // 2+self.yStart-self.radius-3
			self.drawBorder(x0,y0,x1,y1,x2,y2,x3,y3, self.colorC)

	def drawBorder(self, x0,y0,x1,y1,x2,y2,x3,y3, color):
		border = self.border.split(':')
		for i in range(y0, y1):
			_color = self.rainbow(x0, i) if color == "rainbow" else color.color
			_attr = 2 if color == "rainbow" else color.attr
			_bg = self.colorWall if color == "rainbow" else color.bg
			self._screen.print_at(border[4], x0, i, 
				colour=_color, attr=_attr, bg=_bg)
		for i in range(y3, y2):
			_color = self.rainbow(x3, i) if color == "rainbow" else color.color
			_attr = 2 if color == "rainbow" else color.attr
			_bg = self.colorWall if color == "rainbow" else color.bg
			self._screen.print_at(border[4], x3, i, 
				colour=_color, attr=_attr, bg=_bg)
		for i in range(x0, x3):
			_color = self.rainbow(i, y0) if color == "rainbow" else color.color
			_attr = 2 if color == "rainbow" else color.attr
			_bg = self.colorWall if color == "rainbow" else color.bg
			self._screen.print_at(border[5], i, y0, 
				colour=_color, attr=_attr, bg=_bg)
		for i in range(x1, x2):
			_color = self.rainbow(i, y1) if color == "rainbow" else color.color
			_attr = 2 if color == "rainbow" else color.attr
			_bg = self.colorWall if color == "rainbow" else color.bg
			self._screen.print_at(border[5], i, y1, 
				colour=_color, attr=_attr, bg=_bg)
		_color = self.rainbow(x0, y0) if color == "rainbow" else color.color
		_attr = 2 if color == "rainbow" else color.attr
		_bg = self.colorWall if color == "rainbow" else color.bg
		self._screen.print_at(border[0], x0, y0, 
			colour=_color, attr=_attr, bg=_bg)
		_color = self.rainbow(x1, y1) if color == "rainbow" else color.color
		_attr = 2 if color == "rainbow" else color.attr
		_bg = self.colorWall if color == "rainbow" else color.bg
		self._screen.print_at(border[1], x1, y1, 
			colour=_color, attr=_attr, bg=_bg)
		_color = self.rainbow(x2, y2) if color == "rainbow" else color.color
		_attr = 2 if color == "rainbow" else color.attr
		_bg = self.colorWall if color == "rainbow" else color.bg
		self._screen.print_at(border[2], x2, y2, 
			colour=_color, attr=_attr, bg=_bg)
		_color = self.rainbow(x3, y3) if color == "rainbow" else color.color
		_attr = 2 if color == "rainbow" else color.attr
		_bg = self.colorWall if color == "rainbow" else color.bg
		self._screen.print_at(border[3], x3, y3, 
			colour=_color, attr=_attr, bg=_bg)

	def draw(self, x, y, color, char=None, colour=7, bg=0, thin=False):
		# Decide what type of line drawing to use.
		line_chars = (self._screen._uni_line_chars if self._screen._unicode_aware else
			self._screen._line_chars)

		# Define line end points.
		self._x = int(round(self._x * 2, 0))
		self._y = int(round(self._y * 2, 0))
		x0 = self._x
		y0 = self._y
		x1 = int(round(x * 2, 0))
		y1 = int(round(y * 2, 0))

		# Remember last point for next line.
		self._x = x1
		self._y = y1

		# Don't bother drawing anything if we're guaranteed to be off-screen
		if ((x0 < 0 and x1 < 0) or (x0 >= self.w * 2 and x1 >= self.h* 2) or
				(y0 < 0 and y1 < 0) or (y0 >= self.w * 2 and y1 >= self.h * 2)):
			return

		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		sx = -1 if x0 > x1 else 1
		sy = -1 if y0 > y1 else 1

		def _get_start_char(cx, cy):
			needle = self._screen.get_from(cx, cy)
			if needle is not None:
				letter, cfg, _, cbg = needle
				if colour == cfg and bg == cbg and chr(letter) in line_chars:
					return line_chars.find(chr(letter))
			return 0

		def _fast_fill(start_x, end_x, iy):
			next_char = -1
			for ix in range(start_x, end_x):
				if ix % 2 == 0 or next_char == -1:
					next_char = _get_start_char(ix // 2, iy // 2)
				next_char |= 2 ** abs(ix % 2) * 4 ** (iy % 2)
				if ix % 2 == 1:
					self._images[0][ix // 2][iy // 2] = line_chars[next_char]
					_color = self.rainbow(ix // 2, iy // 2) if self.colorC == "rainbow" else color.color
					_attr = 2 if self.colorC == "rainbow" else color.attr
					_bg = self.colorWall if self.colorC == "rainbow" else color.bg
					self._screen.print_at(self._images[0][ix // 2][iy // 2], 
						ix // 2, iy // 2, 
						colour=_color, attr=_attr, bg=_bg)
			if end_x % 2 == 1:
				self._images[0][end_x // 2][iy // 2] = line_chars[next_char]
				_color = self.rainbow(end_x // 2, iy // 2) if self.colorC == "rainbow" else color.color
				_attr = 2 if self.colorC == "rainbow" else color.attr
				_bg = self.colorWall if self.colorC == "rainbow" else color.bg
				self._screen.print_at(self._images[0][end_x // 2][iy // 2], 
					end_x // 2, iy // 2, 
					colour=_color, attr=_attr, bg=_bg)

		def _draw_on_x(ix, iy):
			err = dx
			px = ix - 2
			py = iy - 2
			next_char = 0
			while ix != x1:
				if ix < px or ix - px >= 2 or iy < py or iy - py >= 2:
					px = ix & ~1
					py = iy & ~1
					next_char = _get_start_char(px // 2, py // 2)
				next_char |= 2 ** abs(ix % 2) * 4 ** (iy % 2)
				err -= 2 * dy
				if err < 0:
					iy += sy
					err += 2 * dx
				ix += sx

				#print(px // 2, py // 2)
				ch = char
				if char is None:
					ch = line_chars[next_char]
				self._images[0][px // 2][py // 2] = line_chars[next_char]
				_color = self.rainbow(px // 2, py // 2) if self.colorC == "rainbow" else color.color
				_attr = 2 if self.colorC == "rainbow" else color.attr
				_bg = self.colorWall if self.colorC == "rainbow" else color.bg
				self._screen.print_at(self._images[0][px // 2][py // 2], 
					px // 2, py // 2, 
					colour=_color, attr=_attr, bg=_bg)
					
		def _draw_on_y(ix, iy):
			err = dy
			px = ix - 2
			py = iy - 2
			next_char = 0
			while iy != y1:
				if ix < px or ix - px >= 2 or iy < py or iy - py >= 2:
					px = ix & ~1
					py = iy & ~1
					next_char = _get_start_char(px // 2, py // 2)
				next_char |= 2 ** abs(ix % 2) * 4 ** (iy % 2)
				err -= 2 * dx
				if err < 0:
					ix += sx
					err += 2 * dy
				iy += sy

				ch = char
				if char is None:
					ch = line_chars[next_char]
				self._images[0][px // 2][py // 2] = ch
				_color = self.rainbow(px // 2, py // 2) if self.colorC == "rainbow" else color.color
				_attr = 2 if self.colorC == "rainbow" else color.attr
				_bg = self.colorWall if self.colorC == "rainbow" else color.bg
				self._screen.print_at(self._images[0][px // 2][py // 2], 
					px // 2, py // 2, 
					colour=_color, attr=_attr, bg=_bg)

		if dy == 0 and thin and char is None:
			# Fast-path for polygon filling
			_fast_fill(min(x0, x1), max(x0, x1), y0)
		elif dx > dy:
			_draw_on_x(x0, y0)
			if not thin:
				_draw_on_x(x0, y0 + 1)
		else:
			_draw_on_y(x0, y0)
			if not thin:
				_draw_on_y(x0 + 1, y0)

	@property
	def stop_frame(self):
		return self._stop_frame

	@property
	def frame_update_count(self):
		return 20

class CustomCheckBox(Widget):
	def __init__(self, text, color, label=None, name=None, on_change=None, **kwargs):
		super(CustomCheckBox, self).__init__(name, **kwargs)
		self._text = text
		self._label = label
		self._on_change = on_change
		self.color = color

	def update(self, frame_no):
		self._draw_label()

		# Render this checkbox.
		check_char = u"✓" if self._frame.canvas.unicode_aware else "X"
		colour = self.color.color
		attr = self.color.attr
		bg = self.color.bg
		self._frame.canvas.print_at(
			"[{}] ".format(check_char if self._value else " "),
			self._x + self._offset,
			self._y,
			colour, attr, bg)
		colour = self.color.color
		attr = self.color.attr
		bg = self.color.bg
		self._frame.canvas.print_at(
			self._text,
			self._x + self._offset + 4,
			self._y,
			colour, attr, bg)

	def reset(self):
		pass

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord(" "), 10, 13]:
				# Use property to trigger events.
				self.value = not self._value
			else:
				# Ignore any other key press.
				return event
		elif isinstance(event, MouseEvent):
			# Mouse event - rebase coordinates to Frame context.
			if event.buttons != 0:
				if self.is_mouse_over(event, include_label=False):
					# Use property to trigger events.
					self.value = not self._value
					return None
			# Ignore other mouse events.
			return event
		else:
			# Ignore other events
			return event

		# If we got here, we processed the event - swallow it.
		return None

	def required_height(self, offset, width):
		return 1

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, new_value):
		# Only trigger the notification after we've changed the value.
		old_value = self._value
		self._value = new_value if new_value else False
		if old_value != self._value and self._on_change:
			self._on_change()

class TextView(Widget):
	def __init__(self, height, color, label=None, name=None, as_string=False, line_wrap=False,
				 on_change=None, **kwargs):
		super(TextView, self).__init__(name, **kwargs)
		self._label = label
		self._line = 0
		self._column = 0
		self._start_line = 0
		self._start_column = 0
		self._required_height = height
		self._as_string = as_string
		self._line_wrap = line_wrap
		self._on_change = on_change
		self._reflowed_text_cache = None
		self.string_len = wcswidth

		self.text = ""
		self.color = color
		self._value = []
		
	def update(self, frame_no):
		self._draw_label()
		height = self._h
		dx = dy = 0
		#(colour, attr, bg) = self._pick_colours("edit_text")
		colour = self.color.color
		attr = self.color.attr
		bg = self.color.bg
		for i in range(height):
			self._frame.canvas.print_at(
				" " * self._w,
				self._x + self._offset + dx,
				self._y + i + dy,
				colour, attr, bg)
		
		## Restrict to visible/valid content.
		self._start_line = max(0, min(self._line, len(self._value)-self._h))

		# Render visible portion of the text.
		for i in range(self._start_line, self._start_line + height):
			if i < len(self._value):
				self._frame.canvas.print_at(
					_enforce_width(self._value[i], self._w,
						self._frame.canvas.unicode_aware),
					self._x + self._offset + dx,
					self._y + i - self._start_line + dy,
					colour, attr, bg)

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code == Screen.KEY_UP:
				# Move up one line in text
				self._line = max(0, self._line - 1)
				if self._column >= len(self._value[self._line]):
					self._column = len(self._value[self._line])
			elif event.key_code == Screen.KEY_DOWN:
				# Move down one line in text
				self._line = min(len(self._value) - 1, self._line + 1)
				if self._column >= len(self._value[self._line]):
					self._column = len(self._value[self._line])
			else:
				# Ignore any other key press.
				return event
			return event
		return None

	def required_height(self, offset, width):
		return self._required_height

	@property
	def _reflowed_text(self):
		if self._reflowed_text_cache is None:
			if self._line_wrap:
				self._reflowed_text_cache = []
				limit = self._w - self._offset
				for i, line in enumerate(self._value):
					column = 0
					while self.string_len(line) >= limit:
						sub_string = _enforce_width(
							line, limit, self._frame.canvas.unicode_aware)
						self._reflowed_text_cache.append((sub_string, i, column))
						line = line[len(sub_string):]
						column += len(sub_string)
					self._reflowed_text_cache.append((line, i, column))
			else:
				self._reflowed_text_cache = [(x, i, 0) for i, x in enumerate(self._value)]

		return self._reflowed_text_cache
	def reset(self):
		pass
	@property
	def value(self):
		if self._value is None:
			self._value = [""]
		return "\n".join(self._value) if self._as_string else self._value

	@value.setter
	def value(self, new_value):
		if new_value is None:
			self._value = [""]
		elif self._as_string:
			self._value = new_value.split("\n")
		else:
			self._value = new_value
	
	def setText(self, new_value):
		self.text = new_value
		self.updateValue()

	def updateValue(self):
		self._value = self.text.split("\n")
		_value = []
		for v in self._value:
			_value += [ v[i:i+self._w] for i in range(0, len(v), self._w) ]
		self._value = _value

	@property
	def frame_update_count(self):
		# Force refresh for cursor if needed.
		return 1 if self._has_focus and not self._frame.reduce_cpu else 0

def _find_min_start(text, max_width):
	result = 0
	display_end = wcswidth(text)
	while display_end > max_width:
		result += 1
		display_end -= wcwidth(text[0])
		text = text[1:]
	return result
def _get_offset(text, visible_width):
	result = 0
	width = 0
	for c in text:
		if visible_width - width <= 0:
			break
		result += 1
		width += wcwidth(c)
	if visible_width - width < 0:
		result -= 1
	return result

class CustomText(Widget):
	def __init__(self, color, label=None, name=None, on_change=None, validator=None, hide_char=None,
			**kwargs):
		super(CustomText, self).__init__(name, **kwargs)
		self._label = label
		self._column = 0
		self._start_column = 0
		self._on_change = on_change
		self._validator = validator
		self._hide_char = hide_char
		self.color = color
		self.string_len = wcswidth
		#self.width = self._w - self._offset
	def update(self, frame_no):
		self._draw_label()

		# Calculate new visible limits if needed.
		#self.width = self._w - self._offset
		self._start_column = min(self._start_column, self._column)
		self._start_column += _find_min_start(self._value[self._start_column:self._column + 1],
			self.width)

		colour = self.color.color
		attr = self.color.attr
		bg = self.color.bg
		text = self._value[self._start_column:]
		text = _enforce_width(text, self.width, self._frame.canvas.unicode_aware)
		if self._hide_char:
			text = self._hide_char[0] * len(text)
		text += " " * (self.width - self.string_len(text))
		self._frame.canvas.print_at(
			text,
			self._x + self._offset,
			self._y,
			colour, attr, bg)

		if self._has_focus:
			text_width = self.string_len(text[:self._column - self._start_column])
			self._draw_cursor(
				" " if self._column >= len(self._value) else self._hide_char[0] if self._hide_char
				else self._value[self._column],
				frame_no,
				self._x + self._offset + text_width,
				self._y)

	def reset(self):
		# Reset to original data and move to end of the text.
		self._column = len(self._value)

	def process_event(self, event):
		if isinstance(event, KeyboardEvent):
			if event.key_code == Screen.KEY_BACK:
				if self._column > 0:
					# Delete character in front of cursor.
					self._set_and_check_value("".join([self._value[:self._column - 1],
						self._value[self._column:]]))
					self._column -= 1
			if event.key_code == Screen.KEY_DELETE:
				if self._column < len(self._value):
					self._set_and_check_value("".join([self._value[:self._column],
						self._value[self._column + 1:]]))
			elif event.key_code == Screen.KEY_LEFT:
				self._column -= 1
				self._column = max(self._column, 0)
			elif event.key_code == Screen.KEY_RIGHT:
				self._column += 1
				self._column = min(len(self._value), self._column)
			elif event.key_code == Screen.KEY_HOME:
				self._column = 0
			elif event.key_code == Screen.KEY_END:
				self._column = len(self._value)
			elif event.key_code >= 32:
				# Insert any visible text at the current cursor position.
				self._set_and_check_value(chr(event.key_code).join([self._value[:self._column],
					self._value[self._column:]]))
				self._column += 1
			else:
				# Ignore any other key press.
				return event
		elif isinstance(event, MouseEvent):
			# Mouse event - rebase coordinates to Frame context.
			if event.buttons != 0:
				if self.is_mouse_over(event, include_label=False):
					self._column = (self._start_column +
						_get_offset(self._value[self._start_column:],
							event.x - self._x - self._offset))
					self._column = min(len(self._value), self._column)
					self._column = max(0, self._column)
					return None
			# Ignore other mouse events.
			return event
		else:
			# Ignore other events
			return event

		# If we got here, we processed the event - swallow it.
		return None

	def required_height(self, offset, width):
		return 1

	@property
	def frame_update_count(self):
		# Force refresh for cursor if needed.
		return 5 if self._has_focus and not self._frame.reduce_cpu else 0

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, new_value):
		self._set_and_check_value(new_value, reset=True)

	def _set_and_check_value(self, new_value, reset=False):
		# Only trigger the notification after we've changed the value.
		old_value = self._value
		self._value = new_value if new_value else ""
		if reset:
			self.reset()
		if old_value != self._value and self._on_change:
			self._on_change()
		if self._validator:
			if callable(self._validator):
				self._is_valid = self._validator(self._value)
			else:
				self._is_valid = re.match(self._validator,
					self._value) is not None

