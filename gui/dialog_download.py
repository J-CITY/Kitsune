import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)
from asciimatics.widgets import *

from gui.utils.widget import CustomFileBrowser
from tag_controller import getTagFromPath
from gui.dialog import ADD_END
from gui.utils.utils import ColorTheme, getColor, getAttr, ADD_END, ADD_BEGIN, ADD_AFTER, ADD_BEFORE
from gui.utils.widget import CustomText

class DownloadDialog(Frame):

	def __init__(self, screen, text, url, fname, buttons, 
			presenter=None, on_close=None, has_shadow=False,
			win=""):

		self.fname = fname
		self.url = url
		self.presenter = presenter

		self._buttons = buttons
		self._on_close = on_close
		width = screen.width // 2

		self._message = text
		height = 17
		self.win = win
		# Construct the Frame
		self._data = {"message": self._message}
		super(DownloadDialog, self).__init__(
			screen, height, width, self._data, has_shadow=has_shadow, is_modal=True)

		# Build up the message box
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		
		#TITLE
		if self._message != "":
			layout.add_widget(Label(self._message))
			layout.add_widget(Divider())

		self.browser = CustomFileBrowser(Widget.FILL_FRAME,
			presenter.config.root_dir,
			presenter.config,
			name="save_dir",
			formats=[])
		layout.add_widget(self.browser)
		layout.add_widget(Divider())

		c = presenter.config.dialog.color.split(':')
		tcolor = ColorTheme(getColor(c[0]), getAttr(c[1]), getColor(c[2]))
		self.fileName = CustomText(tcolor, label="File name:",
				name="file_name",
				validator="^[a-zA-Z0-9_]")
		self.fileName.value = self.fname + ".mp3"
		layout.add_widget(self.fileName)
		layout.add_widget(Divider())

		self.playCb = CheckBox("",
				label="Play?",
				name="need_play")
		self.addCurCb = CheckBox("",
				label="Add to current playlist?",
				name="need_play", on_change=self._change_addCurCb)
		self.playCb.disabled = True
		layout.add_widget(self.addCurCb)
		layout.add_widget(self.playCb)
		layout.add_widget(Divider())

		layoutBtns = Layout([1 for _ in buttons])
		self.add_layout(layoutBtns)
		for i, button in enumerate(buttons):
			func = partial(self._destroy, i)
			layoutBtns.add_widget(Button(button, func), i)
		self.fix()

	def _destroy(self, selected):
		if selected == 0:
			fpath = self.browser.getDir()+"\\" + self.fileName.value
			self.presenter.scDownloadName(self.url, fpath, self.fname)
			self.presenter.dbInsertByPath(fpath)
			self.presenter.medialibUpdate()
			if self.addCurCb.value:
				tag = getTagFromPath(fpath)
				self.presenter.mainPlaylistAddSong(ADD_END, self.playCb.value, "current", tag)
			
		self._scene.remove_effect(self)
		if self._on_close:
			self._on_close(-1)

	def _change_addCurCb(self):
		if not self.addCurCb.value:
			if self.playCb != None:
				self.playCb.disabled = True
				self.playCb.value = False
		else:
			self.playCb.disabled = False
		