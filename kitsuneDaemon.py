from core.utils import log, LogLevel
from core.tag_controller import loadPlaylist, savePlaylist
import time
import asyncio
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

class CallbackServer(object):
	def __init__(self):
		self.config = initConfig()
		initDirs(self.config)
		self.db = initDb(self.config)
		self.player = Player(self.config)

	@expose
	def updateDb(self, callback):
		#TODO delete old db if exist
		self.db.walk()
		log(LogLevel.INFO, "Database is updated")
		callback._pyroClaimOwnership()
		callback.default()

	@expose
	@oneway
	def play(self):
		self.player.play()
		print("play")

	@expose
	@oneway
	def pause(self):
		self.player.pause()
		print("pause")

	@expose
	@oneway
	def stop(self):
		self.player.stop()
		print("stop")

	@expose
	@oneway
	def prev(self):
		self.player.prev()
		print("prev")

	@expose
	@oneway
	def next(self):
		self.player.next()
		print("next")

	@expose
	@oneway
	def volumeUp(self):
		self.player.setVolume(self.player.getVolume() + 0.02)
		print("volume+")

	@expose
	@oneway
	def volumeDown(self):
		self.player.setVolume(self.player.getVolume() - 0.02)
		print("volume-")

	@expose
	def getVolume(self):
		print("volume")
		return self.player.getVolume()

	@expose
	@oneway
	def setVolume(self, v):
		return self.player.setVolume(v)
	
	@expose
	@oneway
	def setVolume(self, v):
		return self.player.setVolume(v)

	@expose
	@oneway
	def mute(self):
		return self.player.offOnVolume()
	
	@expose
	def getCurrentSong(self):
		return self.player.getTag()

	@expose
	def add(self, song):
		log(LogLevel.INFO, song)
		path = os.path.join(self.config.cache_folder, 'cache.json')
		playlist = loadPlaylist(path)
		tag = getTagFromPath(song)
		if tag is not None:
			tag.id = playlist.getSize()
			playlist.tracks = playlist.tracks + [tag]
			savePlaylist(playlist, path)
			self.player.playlist = playlist
			log(LogLevel.INFO, "Add song:", path)

	@expose
	def getCurrentPlaylist(self):
		return self.player.playlist

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
#######################################

	@expose
	def getCurrentSong(self):
		return "Green Day - 21"

	@expose
	@oneway
	def setData(self, data):
		print("Data set", data)




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
