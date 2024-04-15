import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gui.utils.widget import CustomFileBrowser
from gui.dialog import ADD_END
from gui.utils.utils import ColorTheme, getColor, getAttr
from gui.utils.widget import CustomText, TextView
from functools import partial
from tag_controller import Tag, getTagFromPath, setTagForPath

CONTROL_INFO = """
<q> <Q> - quit
<i>     - information

"""

CLOCK_INFO = """
CLOCK WINDOW
<space> - on/off seconds in clock

"""

PLAYER_CONTROL_INFO = """
PLAYER CONTROL

<p> - play/pause
<S> - stop
<>> - next song
<<> - previously song
<.> - move ->
<,> - move <-
<-> - volume down
<=> - volume up
<v> - mute
<b> - play mode
<c> - crossfade

"""


MAINPLAYLIST_INFO = """
MAIN PLAYLIST

<Enter> <e> - play song
<j> <k>     - swich song
<d>         - delete song from playlist
<E>         - open menu to add song in any playlist

"""

PLAYLISTS_INFO = """
PLAYLISTS

<e>     - add song to main playlist
<E>     - open menu to add song in any playlist
<l>     - load song from Sound cloud and add to main playlist
<L>     - open menu to load song from Sound cloud
<d>     - delete playlist or song from playlist
<j> <k> - swich songs in playlist
<Enter> - play song

"""

BROWSER_INFO = """
BROWSER

<e>     - add song to main playlist
<E>     - open menu to add song in any playlist

"""

EQUALIZER_INFO = """
EQUALIZER

<Right> <Left> - bar control

"""

MEDIALIB_INFO = """
MEDIA LIBRARY

<e>     - add song to main playlist
<E>     - open menu to add song in any local playlist
<Enter> - play song

"""

SEARCH_INFO = """
SEARCH

<e>     - add song to main playlist
<E>     - open menu to add song in any local playlist
<f>     - like song from Sound cloud
<l>     - load song from Sound cloud and add to main playlist
<L>     - open menu to load song from Sound cloud
<Enter> - play song

"""

VIZUALIZER_INFO = """
VIZUALIZER

<space> - change vizualization

"""


class InfoDialog(Frame):
	def __init__(self, screen, text, buttons, config, has_shadow=False,
			win=""):

		self._buttons = buttons
		width = screen.width // 2
		self._message = text
		height = 17
		self.win = win
		# Construct the Frame
		self._data = {"message": self._message}
		super(InfoDialog, self).__init__(
			screen, height, width, self._data, has_shadow=has_shadow, is_modal=True)

		# Build up the message box
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		
		#TITLE
		_h = height - 4
		if self._message != "":
			layout.add_widget(Label(self._message))
			layout.add_widget(Divider())
			_h -= 2

		c = config.dialog.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.text = TextView(_h, tcolor, name="info")
		self.text._w = screen.width // 2
		self.text._h = _h
		layout.add_widget(self.text)
		layout.add_widget(Divider())
		self.setText()

		layoutBtns = Layout([1 for _ in buttons])
		self.add_layout(layoutBtns)
		for i, button in enumerate(buttons):
			func = partial(self._destroy, i)
			layoutBtns.add_widget(Button(button, func), i)
		self.fix()

	def _destroy(self, selected):
		self._scene.remove_effect(self)
	
	textInfo = {
		'Clock': CLOCK_INFO,
		'Browser': BROWSER_INFO,
		'ArtistInfo': '',
		'Equalizer': EQUALIZER_INFO,
		'Lyrics': '',
		'MainPlaylist': MAINPLAYLIST_INFO,
		'Medialib': MEDIALIB_INFO,
		'Playlists': PLAYLISTS_INFO,
		'Search': SEARCH_INFO,
		'Visualizer': VIZUALIZER_INFO
	}

	def setText(self):
		text = CONTROL_INFO + PLAYER_CONTROL_INFO
		text += self.textInfo[self.win]
		self.text.setText(text)


class TagEditorDialog(Frame):
	def __init__(self, screen, tag, config, has_shadow=False, win=""):

		width = screen.width // 2
		height = 17

		self.tag = tag
		self.win = win
		# Construct the Frame
		self._data = {"message": "Edit tags"}
		super(TagEditorDialog, self).__init__(
			screen, height, width, self._data, has_shadow=has_shadow, is_modal=True)

		# Build up the message box
		layout = Layout([2], fill_frame=True)
		self.add_layout(layout)
		
		layout.add_widget(Divider())

		c = config.dialog.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))

		self.titleText = CustomText(tcolor, label="Title:",
				name="title_text",
				validator="^[a-zA-Z0-9_]")
		layout.add_widget(self.titleText)

		self.albumText = CustomText(tcolor, label="Album:",
				name="album_text",
				validator="^[a-zA-Z0-9_]")
		layout.add_widget(self.albumText)

		self.artistText = CustomText(tcolor, label="Artist:",
				name="artist_text",
				validator="^[a-zA-Z0-9_]")
		layout.add_widget(self.artistText)

		
		layout.add_widget(Divider())
		
		layoutBtns = Layout([1, 1])
		self.add_layout(layoutBtns)
		for i, button in enumerate(["Ok", "Cancel"]):
			func = partial(self._destroy, i)
			layoutBtns.add_widget(Button(button, func), i)
		self.fix()

	def _destroy(self, selected):
		if selected == 0 and self.tag.url is not None and os.path.isfile(self.tag.url):
			self.tag.song = self.titleText.value
			self.tag.album = self.albumText.value
			self.tag.artist = self.artistText.value
			setTagForPath(self.tag.url, self.tag)
		self._scene.remove_effect(self)
