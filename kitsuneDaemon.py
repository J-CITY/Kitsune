from core.utils import log, LogLevel
from core.tag_controller import loadPlaylist, savePlaylist
import time
import asyncio, threading
import collections
from core.db import *
from core.player import Player
try:
	from Pyro5.api import expose, oneway, serve, Daemon, locate_ns
	from pybass.pybass import *
except ImportError or ModuleNotFoundError:
	log(LogLevel.ERROR, "Some important lids are not installed (Pyro5/pybass)")
	exit(1)

async def getLiricsAsinc(callback):
	print("getLiricsAsinc start")
	await asyncio.sleep(1)
	print("5")
	callback._pyroClaimOwnership()
	callback.call("Some lirics")
	print("getLiricsAsinc done")

async def getArtistInfoAsinc(callback):
	print("getLiricsAsinc start")
	await asyncio.sleep(1)
	print("5")
	callback._pyroClaimOwnership()
	callback.call("Some lirics")
	print("getLiricsAsinc done")

CONFIG = 'daemonConfig'

def initConfig():
	import json
	f = open(CONFIG, 'rb')
	data = f.read().decode('utf-8')
	return json.loads(data, object_hook=lambda d: collections.namedtuple('X', d.keys())(*d.values()))

def initDirs(config):
	import pathlib
	pathlib.Path(config.cache_folder).mkdir(parents=True, exist_ok=True) 
	pathlib.Path(config.playlist_folder).mkdir(parents=True, exist_ok=True)

def initDb(config):
	db = Database(config.music_root_dir)
	return db


config = initConfig()
initDirs(config)
db = initDb(config)
player = Player(config)

class CallbackServer(object):
	def __init__(self):
		threadPlayer = threading.Thread(target=self.playerUpdate)
		threadPlayer.daemon = True
		threadPlayer.start()

	def playerUpdate(self):
		player.update()

	@expose
	def updateDb(self, callback):
		#TODO delete old db if exist
		db.walk()
		log(LogLevel.INFO, "Database is updated")
		callback._pyroClaimOwnership()
		callback.default()

	@expose
	@oneway
	def play(self):
		player.play()
		print("play")

	@expose
	@oneway
	def pause(self):
		player.pause()
		print("pause")

	@expose
	@oneway
	def stop(self):
		player.stop()
		print("stop")

	@expose
	@oneway
	def prev(self):
		player.prev()
		print("prev")

	@expose
	@oneway
	def next(self):
		player.next()
		print("next")

	@expose
	@oneway
	def volumeUp(self):
		player.setVolume(player.getVolume() + 0.02)
		print("volume+")

	@expose
	@oneway
	def volumeDown(self):
		player.setVolume(player.getVolume() - 0.02)
		print("volume-")

	@expose
	def getVolume(self):
		print("volume")
		return player.getVolume()

	@expose
	@oneway
	def setVolume(self, v):
		return player.setVolume(v)
	
	@expose
	@oneway
	def setVolume(self, v):
		return player.setVolume(v)

	@expose
	@oneway
	def mute(self):
		return player.offOnVolume()

	@expose
	@oneway
	def move(self, val):
		return player.move(val)
	
	@expose
	def getCurrentSong(self):
		return player.getTag()

	@expose
	def changeCrossfade(self):
		player.crossfade = not player.crossfade

	@expose
	def changeMode(self):
		player.mode = (player.mode+1) % 5

	@expose
	def getMode(self):
		return player.mode

	@expose
	def getCrosfade(self):
		return player.crossfade

	@expose
	def add(self, song):
		log(LogLevel.INFO, song)
		path = os.path.join(config.cache_folder, 'cache.json')
		playlist = loadPlaylist(path)
		tag = getTagFromPath(song)
		if tag is not None:
			tag.id = playlist.getSize()
			playlist.tracks = playlist.tracks + [tag]
			savePlaylist(playlist, path)
			player.playlist = playlist
			log(LogLevel.INFO, "Add song:", path)

	@expose
	def getCurrentPlaylist(self):
		return player.playlist

	@expose
	@oneway
	def getLyrics(self, callback):
		print("getLirics start")
		asyncio.run(getLiricsAsinc(callback))
		#callback._pyroClaimOwnership()
		#callback.call("Some lirics")
		print("getLirics dnoe")

	@expose
	@oneway
	def getArtistInfo(self, callback):
		print("getLirics start")
		asyncio.run(getArtistInfoAsinc(callback))
		#callback._pyroClaimOwnership()
		#callback.call("Some lirics")
		print("getLirics dnoe")

	@expose
	def playerPlayById(self, id):
		if len(player.playlist.tracks) > id:
			tag = player.playlist.tracks[id]
			tag.length = player.getLen()
			player.playlistId = id
			player.stop()
			player.play()
			return tag
		tag = player.getTag()
		tag.length = player.getLen()
		return tag

	# TODO: think this is should delete
	@expose
	@oneway
	def playerSetPlaylistId(self, id):
		player.playlistId = id

	@expose
	def playerSwap(self, _from, _to):
		if _from == _to:
			return
		ida = player.playlist.tracks[_from].id
		idb = player.playlist.tracks[_to].id
		itm = player.playlist.tracks[_from]
		player.playlist.tracks[_from] = player.playlist.tracks[_to]
		player.playlist.tracks[_to] = itm
		player.playlist.tracks[_from].id = ida
		player.playlist.tracks[_to].id = idb

	@expose
	def playerGetPlaylist(self):
		return player.playlist

	@expose
	def playerGetCurrentTag(self):
		return player.playlist.tracks[player.playlistId]

	@expose
	def playerGetCurrentTagWithLength(self):
		tag = player.playlist.tracks[player.playlistId]
		tag.length = player.getLen()
		return tag

	@expose
	def playerDelete(self, id):
		player.playlist.tracks = player.playlist.tracks[0:id]+player.playlist.tracks[id+1:]
		for i in player.playlist.tracks[id:]:
			i.id -= 1

	@expose
	def playerGetIsPlay(self):
		return player.getIsPlay()

	@expose
	def playerGetSongLength(self):
		return player.getLen()
	
	@expose
	def playerGetCurrentSongProgress(self):
		return player.getBuf()

	@expose
	def getListOfPlaylists(self):
		arr = os.listdir(config.playlist_folder)
		return arr

	@expose
	@oneway
	def setUpdatePlayerItemCb(self, cb):
		#cb._pyroClaimOwnership()
		#print(2)
		#cb.updatePlayerItemCb()
		#print(3)
		player.setUpdatePlayerItemCb(cb)

#daemon = Daemon()
#ns = locate_ns()
#uri = daemon.register(CallbackServer)
#ns.register("example.callback", uri)
#print("Ready.")
#daemon.requestLoop()

serve({
	CallbackServer: "kitsune.music.daemon"
})

#import Pyro5.api
#
#@Pyro5.api.expose
#class GreetingMaker(object):
#    def get_fortune(self, name):
#        return "Hello, {0}. Here is your fortune message:\n" \
#               "Tomorrow's lucky number is 12345678.".format(name)
#
#daemon = Pyro5.server.Daemon()         # make a Pyro daemon
#ns = Pyro5.api.locate_ns()             # find the name server
#uri = daemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
#ns.register("example.greeting", uri)   # register the object with a name in the name server
#
#print("Ready.")
#daemon.requestLoop()
