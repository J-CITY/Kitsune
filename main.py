
#TODO add offline mode
from asciimatics.event import KeyboardEvent
from asciimatics.widgets import *
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene

import sys
import os
try:
	import magic
except ImportError:
	pass

from gui.bar import *
from gui.mainplaylist import *
from gui.browser import *
from gui.clock import *
from gui.equalizer import *
from gui.playlists import *
from gui.visualization import *
from gui.medialib import *
from gui.artistInfo import *
from gui.lyrics import *
from player import Player
from gui.presenter import *
from gui.search import *

from lastfm_client import *
from lyricsWiki import *

from soundcloud_client import SoundcloudClient
from yandexMusicClient import YandexMusicClient

from db import *

SCR = 1


f = open('config', 'rb')
data = f.read().decode('utf-8')

config = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
import pathlib
pathlib.Path(config.cash_folder).mkdir(parents=True, exist_ok=True) 
pathlib.Path(config.playlist_folder).mkdir(parents=True, exist_ok=True)

if config.useInternet:
	canConnectToSC = True
	try:
		if (config.sound_cloud.client_id != ''):
			sc = SoundcloudClient(
				config.sound_cloud.client_id,
				config.sound_cloud.client_secret,
				config.sound_cloud.username,
				config.sound_cloud.password,
				config.sound_cloud.bpm,
				config.sound_cloud.search_pages)
		else:
			sc = SoundcloudClient()
	except:
		canConnectToSC = False
if config.useInternet:
	if (config.lastfm.apikey != ''):
		lastfm = Lastfm(config.lastfm.apikey, config.lastfm.lang)
	else:
		lastfm = Lastfm()
	if (config.lirycsApi.apikey != ''):
		lyricsWiki = LyricsWiki(config.lirycsApi.apikey)
	else:
		lyricsWiki = LyricsWiki()


upBar = Bar()
upBar.parse(config, UP_BAR)

downBar = Bar()
downBar.parse(config, DOWN_BAR)


player = Player(config)
presenter = Presenter(config)
presenter.setPlayer(player)
if config.useInternet:
	presenter.setSoundCloud(sc)
	presenter.setLastfm(lastfm)
	presenter.setLyricsWiki(lyricsWiki)
	lastfm.setPresenter(presenter)

if config.useInternet:
	if (config.yandex_music.token != ''):
		yandexMusicClient = YandexMusicClient(config.yandex_music.token)
	else:
		yandexMusicClient = YandexMusicClient()
	yandexMusicClient.setPresenter(presenter)
	presenter.setYandexMusicClient(yandexMusicClient)

db = Database()
db.PATH = config.root_dir
presenter.setDb(db)


def init(screen, old_scene):
	if config.useInternet:
		sc.setPresenter(presenter)

	browser = BrowserFrame(screen, upBar, downBar, config)
	browser.setPresenter(presenter)
	
	medialib = MedialibFrame(screen, upBar, downBar, config)
	medialib.setPresenter(presenter)

	playlists = PlaylistsFrame(screen, upBar, downBar, config)
	playlists.setPresenter(presenter)

	equalizer = EqualizerFrame(screen, upBar, downBar, config)
	equalizer.setPresenter(presenter)

	viz = VisualizationFrame(screen, upBar, downBar, config)
	viz.setPresenter(presenter)

	clock = ClockFrame(screen, upBar, downBar, config)
	clock.setPresenter(presenter)

	if config.useInternet:
		artistinfo = ArtistInfoFrame(screen, upBar, downBar, config)
		artistinfo.setPresenter(presenter)
	if config.useInternet:
		lyrics = LyricsFrame(screen, upBar, downBar, config)
		lyrics.setPresenter(presenter)

	search = SearchFrame(screen, upBar, downBar, config)
	search.setPresenter(presenter)
	
	mainplaylist = MainPlaylistFrame(screen, upBar, downBar, config)
	mainplaylist.setPresenter(presenter)

	presenter.setBrowser(browser)
	presenter.setMainPlaylist(mainplaylist)
	presenter.setPlaylists(playlists)
	presenter.setEqualizer(equalizer)
	presenter.setClock(clock)
	presenter.setUpBar(upBar)
	presenter.setDownBar(downBar)
	presenter.setVisualization(viz)
	presenter.setMedialib(medialib)
	if config.useInternet:
		presenter.setArtistInfo(artistinfo)
		presenter.setLyrics(lyrics)
	presenter.setSearch(search)

	player.setPresenter(presenter)

	presenter.run()


	screens = [Scene([mainplaylist], -1, name="MainPlaylist"),
				Scene([browser], -1, name="Browser"),
				Scene([medialib], -1, name="Medialib"),
				Scene([playlists], -1, name="Playlists"),
				Scene([equalizer], -1, name="Equalizer"),
				Scene([viz], -1, name="Visualizer")]
	if config.useInternet:
		screens.append(Scene([artistinfo], -1, name="ArtistInfo"))
		screens.append(Scene([lyrics], -1, name="Lyrics"))
	screens.append(Scene([clock], -1, name="Clock"))
	screens.append(Scene([search], -1, name="Search"))

	screen.play(screens,
				stop_on_resize=True, start_scene=old_scene)


def openFile(fname):
	path = config.cash_folder + "/cash.json" if config.cash_folder[len(config.cash_folder)-1] != "/" else "cash.json"
	playlist = loadPlaylist(path)
	tag = getTagFromPath(fname)
	tag.id = 0
	for t in playlist:
		t.id += 1
	playlist = [tag] + playlist
	savePlaylist(playlist, path)
	player.playlist = playlist
	#player.play()

def printHelp():
	from gui.dialog_info import (CONTROL_INFO, CLOCK_INFO, PLAYER_CONTROL_INFO,
		MAINPLAYLIST_INFO, PLAYLISTS_INFO, BROWSER_INFO, EQUALIZER_INFO,
		MEDIALIB_INFO, SEARCH_INFO, VIZUALIZER_INFO)

	text = "-db - create db (need delete old db)\n"+\
		"-h --help - print help\n" + CONTROL_INFO + "\n"+ CLOCK_INFO + "\n"+ PLAYER_CONTROL_INFO + "\n"+\
		MAINPLAYLIST_INFO + "\n"+ PLAYLISTS_INFO + "\n"+ BROWSER_INFO + "\n"+ EQUALIZER_INFO + "\n"+\
		MEDIALIB_INFO + "\n"+ SEARCH_INFO + "\n"+ VIZUALIZER_INFO + "\n"
	print(text)

def createDb():
	#TODO delete old db if exist
	db.walk()

def argParse():
	lenargs = len(sys.argv)
	if lenargs == 2 and (sys.argv[1] != "-h" and sys.argv[1] != "--help" and
		sys.argv[1] != "-db"):
		#TODO format test
		openFile(sys.argv[1])
	elif lenargs == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
		printHelp()
		sys.exit()
	elif lenargs == 2 and sys.argv[1] == "-db":
		createDb()
		sys.exit()

argParse()


last_scene = None
while True:
	try:
		Screen.wrapper(init, catch_interrupt=False, arguments=[last_scene])

		path = config.cash_folder + "/cash.json" if config.cash_folder[len(config.cash_folder)-1] != "/" else "cash.json"
		savePlaylist(player.playlist, path)

		player.destructor()
		sys.exit(0)
	except ResizeScreenError as e:
		last_scene = e.scene




