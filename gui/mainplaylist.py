import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from asciimatics.widgets import *
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

from core.utils import getColor, getAttr, ColorTheme, MusicAddPolitics
from gui.utils.widget import CustomFrame, CustomMainPlaylistBox, ImageView
from gui.dialog import *
from gui.dialog_info import InfoDialog
from core.strings import FRAME_MAIN_PLAYLIST

class MainPlaylistFrame(CustomFrame):
	def __init__(self, screen, upBar, downBar, presenter):
		super(MainPlaylistFrame, self).__init__(
			screen, screen.height, screen.width, has_border=False, name=FRAME_MAIN_PLAYLIST, upBar=upBar, downBar=downBar, bg=getColor(presenter.config.bg_color))

		self.showImage = presenter.config.main_playlist.image_show
		self.image = ImageView(self.screen.height-self.dup-self.ddown, ColorTheme(0, 2, self.bgColor), name="art")
		self.image.screen = screen
		self.createTable(presenter)

		self.createLayout()
		self.setPresenter(presenter)

	def createTable(self, presenter):
		columnSize = []
		colors = []
		choiceColors = []
		playColors = []
		data = []
		titles = []
		for itm in presenter.config.main_playlist.columns:
			data.append(itm.data)
			columnSize.append(itm.width)
			c = itm.color.split(':')
			colors.append(ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])))
			c = itm.choice_color.split(':')
			choiceColors.append(ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])))
			c = itm.play_color.split(':')
			playColors.append(ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2])))
			if presenter.config.main_playlist.title:
				titles.append(itm.title)
		
		self.table = CustomMainPlaylistBox(Widget.FILL_FRAME,
			columnSize,
			colors,
			choiceColors,
			playColors,
			data,
			[],
			titles,
			name="main_playlist",
			on_select=self._play)
		self.table.choiceCh = presenter.config.main_playlist.choice_char
		self.table.itemCh = presenter.config.main_playlist.item_char
		self.table.playCh = presenter.config.main_playlist.play_char

	def createLayout(self):
		scrW = self.image.screen.width
		self.image.clear()
		self._layouts = []
		self.addUpBar()
		if self.showImage:
			col1sz = 20 + 5*2 if scrW > 20 + 5 * 2 else 0
			self.layout = Layout([col1sz, scrW - col1sz], fill_frame=True)
			self.add_layout(self.layout)
			self.layout.add_widget(self.image, 0)
			self.layout.add_widget(self.table, 1)
		else:
			self.layout = Layout([1], fill_frame=True)
			self.add_layout(self.layout)
			self.layout.add_widget(self.table, 0)
		self.addDownBar()
		self.fix()

	def process_event(self, event):
		# Do the key handling for this Frame.
		if isinstance(event, KeyboardEvent):
			self.swichWindow(self.presenter, event)
			if event.key_code in [ord('e')]:
				self.table.playId = self.table.value
				self.presenter.playerPlayById(self.table.value)
			if event.key_code in [ord('j')]:#swap prev
				_from = self.table._line
				_to = self.table._line-1 if self.table._line > 0 else self.table._line
				self.presenter.playerSwap(_from, _to)
				self.table._line = max(0, self.table._line - 1)
				self.table.value = self.table._options[self.table._line][1]
			if event.key_code in [ord('k')]:#swap next
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
							("At the end of playlist", MusicAddPolitics.ADD_END),
							("At the beginning of playlist", MusicAddPolitics.ADD_BEGIN)
						],
						playlistLists = pls,
						needNewPlaylist = True,
						needListAdd = True,
						needListPlaylists = True,
						needPlayCb = False,
						presenter=self.presenter, win="MainPlaylist"))
			if event.key_code in [ord(' ')]:
				self.showImage = not self.showImage
				self.createLayout()
				return None

			self.presenter.playerEventControl(event)
			
		# Now pass on to lower levels for normal handling of the event.
		return super(MainPlaylistFrame, self).process_event(event)

	def setPresenter(self, p):
		self.presenter = p
		self.presenter.addFrame(self.frameName, self)
		self.presenter.mainPlaylistUpdateList()

	def getCurrentLineId(self):
		return self.table._line

	def _play(self):
		self.presenter.mainPlaylistSetPlayId(self.table._line)

	def updateCover(self):
		if self.showImage == False:
			return True
		
		song = self.presenter.song
		if not song:
			return True

		path = "cache/" + song.artist + '_' + song.album + '_album.png'
		if os.path.exists(path):
			dup = len(self.upBar.layouts)
			self.image.setImage(path, self.presenter.config.main_playlist.image_size, 
					   self.presenter.config.main_playlist.image_offset, 
					   dup + self.presenter.config.main_playlist.image_offset)
			return True
		return False

	def updateCoverCb(self, path, artist, song):
		if path == '':
			path = "cache/defAlbum.ico"
		if self.presenter.song and self.presenter.song.artist == artist and self.presenter.song.song == song:
			dup = len(self.upBar.layouts)
			self.image.setImage(path, self.presenter.config.main_playlist.image_size, 
					   self.presenter.config.main_playlist.image_offset, 
					   dup + self.presenter.config.main_playlist.image_offset)
		else:
			self.presenter.mainPlaylistUpdateCover()