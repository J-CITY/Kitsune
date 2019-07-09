import os, sys
parentPath = os.path.abspath("../../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
	
from asciimatics.widgets import *

ADD_END = 0
ADD_BEGIN = 1
ADD_AFTER = 2
ADD_BEFORE = 3

def getColor(c):
	return {
		'black': 0,
		'red': 1,
		'green': 2,
		'yellow': 3,
		'blue': 4,
		'magenta': 5,
		'cyan': 6,
		'white': 7
	}[c]
	
def getAttr(a):
	return {
		'bold': 1,
		'normal': 2,
		'reverse': 3,
		'underline': 4
	}[a]

class ColorTheme:
	def __init__(self, color, attr, bg):
		self.color = color
		self.attr = attr
		self.bg = bg

def split_text(text, width, height, unicode_aware=True):
	tokens = text.split(" ")
	result = []
	current_line = ""
	string_len = wcswidth if unicode_aware else len
	for token in tokens:
		for i, line_token in enumerate(token.split("\n")):
			if string_len(current_line + line_token) > width or i > 0:
				result.append(current_line.rstrip())
				current_line = line_token + " "
			else:
				current_line += line_token + " "

	# Add any remaining text to the result.
	result.append(current_line.rstrip())

	# Check for a height overrun and truncate.
	if len(result) > height:
		result = result[:height]
		result[height - 1] = result[height - 1][:width - 3] + "..."

	for i, line in enumerate(result):
		if len(line) > width:
			result[i] = line[:width - 3] + "..."
	return result

def _find_min_start(text, max_width, unicode_aware=True, at_end=False):
	result = 0
	string_len = wcswidth if unicode_aware else len
	char_len = wcwidth if unicode_aware else lambda x: 1
	display_end = string_len(text)
	while display_end > max_width:
		result += 1
		display_end -= char_len(text[0])
		text = text[1:]
	if at_end and display_end == max_width:
		result += 1
	return result


import json
from collections import namedtuple
from tag_controller import *

def savePlaylist(pl, path):
	saveList = []
	for i, t in enumerate(pl):
		_t = {
			'url': t.url,
			'artist': t.artist if t.artist != None else "",
			'album': t.album if t.album != None else "",
			'song': t.song if t.song != None else "",
			'fileName': t.fileName if t.fileName != None else "",
			'year': t.year if t.year != None else "",
			'genre': t.genre if t.genre != None else "",
			'coverart': t.coverart if t.coverart != None else "",
			'length': t.length if t.length != None else 0,
			'curLength': t.curLength if t.curLength != None else 0,
			'id': i,
			'globalId': t.globalId
		}
		saveList.append(_t)

	
	outfile = open(path, 'w')
	json.dump({'pl': saveList}, outfile)

def loadPlaylist(path):
	print(path)
	try:
		f = open(path, 'r')
	except IOError as e:
		return []
	else:
		data = f.read()
		#print(data)
		jspl = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

		res = []
		for e in jspl.pl:
			#print(e)
			t = Tag()
			t.url = e.url
			t.artist = e.artist
			t.album = e.album
			t.song = e.song
			t.fileName = e.fileName
			t.year = e.year
			t.genre = e.genre
			t.coverart = e.coverart
			t.length = e.length
			t.curLength = e.curLength
			t.id = e.id
			t.globalId = e.globalId
			res.append(t)
		return res
