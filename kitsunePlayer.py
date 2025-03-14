import sys
from asciimatics.widgets import *
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from collections import namedtuple
from gui.bar import *
from gui.mainplaylist import *
from gui.browser import *
from gui.medialib import *
from gui.clock import *
from gui.equalizer import *
from gui.playlists import *
from gui.visualization import *
from gui.search import *
from gui.artistInfo import *
from gui.lyrics import *
from gui.presenter import *
from core.strings import *

CONFIG_PATH = 'config'

config = None
presenter = None

#TODO: async artist bio, cover, load ym playlist
#TODO reg custom colors

def init(screen, oldScene):
	global config
	global presenter

	upBar = Bar()
	upBar.parse(config, UP_BAR)

	downBar = Bar()
	downBar.parse(config, DOWN_BAR)

	#medialib = MedialibFrame(screen, upBar, downBar, config)
	#medialib.setPresenter(presenter)
	#
	#playlists = PlaylistsFrame(screen, upBar, downBar, config)
	#playlists.setPresenter(presenter)
	#
	#equalizer = EqualizerFrame(screen, upBar, downBar, config)
	#equalizer.setPresenter(presenter)
	#
	#viz = VisualizationFrame(screen, upBar, downBar, config)
	#viz.setPresenter(presenter)
	#
	#clock = ClockFrame(screen, upBar, downBar, config)
	#clock.setPresenter(presenter)
	#
	#search = SearchFrame(screen, upBar, downBar, config)
	#search.setPresenter(presenter)
	
	presenter.setUpBar(upBar)
	presenter.setDownBar(downBar)

	if FRAME_MAIN_PLAYLIST not in config.screens:
		log(LogLevel.ERROR, "Screen 'MainPlaylist' must be in config.screens")
		exit(1)

	screens = []
	for screenName in config.screens:
		s = eval(screenName + 'Frame')(screen, upBar, downBar, presenter)
		screens.append(Scene([s], -1, name=screenName))

	presenter.setFrameToBars('MainPlaylist')

	presenter.frames[FRAME_LYRICS].text.screen = screen

	screen.play(screens, stop_on_resize=True, start_scene=oldScene)

def printHelp():
	from gui.dialog_info import (CONTROL_INFO, CLOCK_INFO, PLAYER_CONTROL_INFO,
		MAINPLAYLIST_INFO, PLAYLISTS_INFO, BROWSER_INFO, EQUALIZER_INFO,
		MEDIALIB_INFO, SEARCH_INFO, VIZUALIZER_INFO)

	text = "-db - create db (need delete old db)\n"+\
		"-h --help - print help\n" + CONTROL_INFO + "\n"+ CLOCK_INFO + "\n"+ PLAYER_CONTROL_INFO + "\n"+\
		MAINPLAYLIST_INFO + "\n"+ PLAYLISTS_INFO + "\n"+ BROWSER_INFO + "\n"+ EQUALIZER_INFO + "\n"+\
		MEDIALIB_INFO + "\n"+ SEARCH_INFO + "\n"+ VIZUALIZER_INFO + "\n"
	print(text)

def argParse():
	lenargs = len(sys.argv)
	if lenargs == 2 and sys.argv[1] != "-h" and sys.argv[1] != "--help":
		presenter.openMusicFile(sys.argv[1])
	elif lenargs == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
		printHelp()
		sys.exit()

def main():
	global config
	global presenter
	import json
	f = open(CONFIG_PATH, 'rb')
	data = f.read().decode('utf-8')
	config = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
	
	presenter = Presenter(config)
	# start bar loops in new threads
	presenter.run()
	argParse()

	lastScene = None
	while True:
		try:
			Screen.wrapper(init, catch_interrupt=False, arguments=[lastScene])
			presenter.playerSavePlaylist()
			sys.exit(0)
		except ResizeScreenError as e:
			lastScene = e.scene

if __name__ == "__main__":
	main()
