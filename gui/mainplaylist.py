import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.utils import getColor, getAttr, ColorTheme
from gui.utils.widget import CustomFrame, CustomMainPlaylistBox

from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene
from gui.dialog import *
from gui.dialog_info import InfoDialog

class MainPlaylistFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, config):
		super(MainPlaylistFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name="MainPlaylist", bg=getColor(config.bg_color))

		self.upBar = upBar
		self.downBar = downBar

		i = 0
		for l in upBar.layouts:
			_l = Layout([l[0],l[1],l[2]])
			self.add_layout(_l)
			_l.add_widget(upBar.lables[i], 0)
			_l.add_widget(upBar.lables[i+1], 1)
			_l.add_widget(upBar.lables[i+2], 2)
			i+=3
		
		layout = Layout([1], fill_frame=True)
		self.add_layout(layout)

		csize = []
		colors = []
		ccolors = []
		pcolors = []
		data = []
		titles = []
		for itm in config.main_playlist.columns:
			data.append(itm.data)
			csize.append(itm.width)
			c = itm.color.split(':')
			colors.append(ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])))
			c = itm.choice_color.split(':')
			ccolors.append(ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])))
			c = itm.play_color.split(':')
			pcolors.append(ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])))
			if config.main_playlist.title:
				titles.append(itm.title)
		
		self.table = CustomMainPlaylistBox(Widget.FILL_FRAME,
			csize,
			colors,
			ccolors,
			pcolors,
			data,
			[],
			titles,
			name="main_playlist",
			on_select=self._play)
		self.table.choiceCh = config.main_playlist.choice_char
		self.table.itemCh = config.main_playlist.item_char
		self.table.playCh = config.main_playlist.play_char

		layout.add_widget(self.table)

		i = 0
		for l in downBar.layouts:
			_l = Layout([l[0],l[1],l[2]])
			self.add_layout(_l)
			_l.add_widget(downBar.lables[i], 0)
			_l.add_widget(downBar.lables[i+1], 1)
			_l.add_widget(downBar.lables[i+2], 2)
			i+=3
		self.fix()

	def process_event(self, event):
		# Do the key handling for this Frame.
		if isinstance(event, KeyboardEvent):
			if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
				raise StopApplication("User quit")
			self.swichWindow(self.presenter, event)
			if event.key_code in [ord('e')]:
				self.presenter.mainPlaylistSetPlayId(self.table.value)
				self.presenter.playerPlayById(self.table.value)
			if event.key_code in [ord('j')]:#swap
				_from = self.table._line
				_to = self.table._line-1 if self.table._line > 0 else self.table._line
				self.presenter.playerSwap(_from, _to)
				self.table._line = max(0, self.table._line - 1)
				self.table.value = self.table._options[self.table._line][1]
			if event.key_code in [ord('k')]:#swap
				_from = self.table._line
				_to = self.table._line+1 if self.table._line < len(self.table._options)-1 else self.table._line
				self.presenter.playerSwap(_from, _to)
				self.table._line = min(len(self.table._options) - 1, self.table._line + 1)
				self.table.value = self.table._options[self.table._line][1]
			if event.key_code in [ord('d')]:#delete
				_id = self.table._line
				self.presenter.playerDelete(_id)
				if len(self.table._options) > 0:
					self.table._line = min(len(self.table._options) - 1, self.table._line + 1)
					self.table.value = self.table._options[self.table._line][1]
					_new_options = []
					for i, e in enumerate(self.table._options):
						v = e[0]
						v[0] = str(i)
						_new_options.append((v, i))
					self.table._options = _new_options

			if event.key_code in [ord('E')]:
				pls = self.presenter.getListOfPlaylists()
				for i, e in enumerate(pls):
					pls[i] = (e, i)
				self._scene.add_effect(
					AddMusicDialog(self._screen, 
						"Save playlist", 
						["OK", "Cancel"], 
						addList = [
							("At the end of playlist", ADD_END),
							("At the beginning of playlist", ADD_BEGIN)
						],
						playlistLists = pls,
						needNewPlaylist = True,
						needListAdd = True,
						needListPlaylists = True,
						needPlayCb = False,
						presenter=self.presenter, win="MainPlaylist"))
			if event.key_code in [ord("i")]:
				self._scene.add_effect(
					InfoDialog(self._screen, 
						"Info",
						["OK"],
						config=self.presenter.config, win=self.frameName))

			self.presenter.playerEventControl(event)
			
		# Now pass on to lower levels for normal handling of the event.
		return super(MainPlaylistFrame, self).process_event(event)

	def setPresenter(self, p):
		self.presenter = p

	def getId(self):
		return self.table._line

	def _play(self):
		self.presenter.mainPlaylistSetPlayId(self.table._line)
		self.presenter.playerPlayById(self.table._line)
