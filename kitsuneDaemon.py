from core.utils import log, LogLevel
from core.tag_controller import loadPlaylist, savePlaylist
import time
import asyncio, threading
import collections
from core.db import *
from core.player import Player
from core.lyricsWiki import LyricsWiki
from core.lastfm_client import Lastfm
from core.yandexMusicClient import YandexMusicClient
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
	pathlib.Path(config.download_folder).mkdir(parents=True, exist_ok=True)
	pathlib.Path(config.playlist_folder).mkdir(parents=True, exist_ok=True)

def initDb(config):
	db = Database(config.music_root_folder)
	return db

def initLyrics(config):
	lyrics = LyricsWiki(config.lirycs.apikey)
	return lyrics

def initLastfm(config):
	lastfm = Lastfm(config.lastfm.apikey)
	return lastfm

def initYandexMusic(config):
	ym = YandexMusicClient(config.yandex_music.token)
	player.setGetYandexMusicUrlCb(ym.getTrackUrl)
	return ym

config = initConfig()
initDirs(config)
db = initDb(config)
player = Player(config)
lyrics = initLyrics(config)
lastfm = initLastfm(config)
yaMusic = initYandexMusic(config)

def playerUpdate():
	player.update()


class CallbackServer(object):
	def __init__(self):
		pass
		#threadPlayer = threading.Thread(target=self.playerUpdate)
		#threadPlayer.daemon = True
		#threadPlayer.start()

	@expose
	@oneway
	def updateDb(self, callback):
		global db
		# remove old db
		path = db.dbPath
		db = None
		os.remove(path)
		# create new db
		db = initDb(config)
		# fill
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
		#print("volume")
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
	@oneway
	def moveDirection(self, val):
		return player.moveDirection(val)

	@expose
	def getCurrentSong(self):
		return player.getTag()

	@expose
	def changeCrossfade(self):
		player.crossfade = not player.crossfade

	@expose
	def changeMode(self):
		player.nextMode()

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
	def playerSetCurrentPlaylistTracks(self, pl):
		print('playerSetCurrentPlaylistTracks',pl[-1].type)
		player.playlist.tracks = pl
	
	@expose
	def playerGetCurrentSongProgress(self):
		return player.getBuf()

	@expose
	def getListOfPlaylists(self):
		arr = os.listdir(config.playlist_folder)
		return arr

	@expose
	def getPlaylistDir(self):
		return config.playlist_folder

	@expose
	def getUseInternet(self):
		return config.use_internet

	@expose
	def getMusicRootDir(self):
		return config.music_root_folder

	@expose
	def getDownloadDir(self):
		return config.download_folder

	@expose
	def getCacheDir(self):
		return config.cache_folder

	@expose
	def dbSelect(self, query):
		return db.select(query)

	@expose
	def dbSearch(self, query):
		return db.search(query)

	@expose
	def dbExecute(self, text, params):
		return db.execute(text, params)

	@expose
	def dbInsertByPath(self, query):
		return db.insertByPath(query)

	@expose
	@oneway
	def eqSetEqParams(self):
		player.setEqParams()

	@expose
	@oneway
	def eqSetLevelParam(self, param):
		player.setEqLevelParam(param)
		player.setEqParams()

	@expose
	@oneway
	def eqSetSpeedParam(self ,param):
		player.setEqSpeedParam(param)
		player.setEqParams()

	@expose
	@oneway
	def eqSetBassParam(self, param):
		player.setEqBass(param)
		player.setEqParams()

	@expose
	@oneway
	def eqSetEchoParam(self, param):
		player.setEqEcho(param)
		player.setEqParams()

	@expose
	@oneway
	def eqSetChorusParam(self, param):
		player.setEqChorus(param)
		player.setEqParams()

	@expose
	@oneway
	def eqSetFlangeParam(self, param):
		player.setEqFlange(param)
		player.setEqParams()

	@expose
	@oneway
	def eqSetReverbParam(self, param):
		player.setEqReverb(param)
		player.setEqParams()

	@expose
	def playerGetWaveData(self, isSterio, col):
		return player.getWaveData(isSterio, col)

	@expose
	def playerGetFFTData(self, isSterio, col):
		return player.getFFTData(isSterio, col)

	@expose
	def lyricsGetSongLyrics(self, artist, song, ymId=None):
		if artist == "" or song == "":
			return ''

		text = ''
		if ymId and yaMusic:
			text = yaMusic.getLyrics(ymId)
			if len(text > 0):
				return text

		if lyrics:
			text = lyrics.getLyrics(artist, song)
		return text

	@expose
	def lastfmGetArtistBio(self, artist):
		if lastfm is None:
			return ""
		if artist == "":
			return ""
		#if not config.use_internet:
		#	return ""
		text = lastfm.getArtistBio(artist)
		return text
	
	@expose
	def lastfmGetCover(self, artist, song, ymId = None):
		if artist == '' or song == '':
			return ''
		path = ''
		if ymId and yaMusic:
			path = yaMusic.saveCover(ymId)
			if len(path > 0):
				return path
		if lastfm:
			path = lastfm.saveAlbumArt(artist, song)
		return path

	@expose
	def yandexMusicGetFavorites(self):
		if yaMusic is None:
			return ""
		return yaMusic.getFavorite()

	@expose
	def yandexMusicGetPlaylists(self):
		if yaMusic is None:
			return []
		return yaMusic.getPlaylists()

	@expose
	def yandexMusicGetPlaylist(self, name):
		if yaMusic is None:
			return None
		return yaMusic.getPlaylist(name)

	@expose
	def yandexMusicGetMusicTrack(self, id):
		if yaMusic is None:
			return None
		return yaMusic.getTrack(id)

	@expose
	def yandexMusicGetTracks(self, ids):
		if yaMusic is None:
			return []
		print("yandexMusicGetTracks")
		return yaMusic.getTracks(ids)

	@expose
	def yandexMusicGetTrackUrl(self, id):
		if yaMusic is None:
			return None
		return yaMusic.getTrackUrl(id)

	@expose
	def yandexMusicIsInit(self):
		if yaMusic is None:
			return False
		return yaMusic.isInitial()
	
	@expose
	@oneway
	def yandexMusicDownloadTrack(self, id):
		if yaMusic is None:
			return
		path = yaMusic.downloadTrack(id, config.download_folder)
		if len(path) > 0:
			# Add to medialib
			db.insertByPath(path)


#daemon = Daemon()
#ns = locate_ns()
#uri = daemon.register(CallbackServer)
#ns.register("example.callback", uri)
#print("Ready.")
#daemon.requestLoop()

from Pyro5.api import register_dict_to_class, register_class_to_dict
register_class_to_dict(Playlist, playlist_class_to_dict)
register_dict_to_class("core.tag_controller.Playlist", playlist_dict_to_class)
register_class_to_dict(Tag, tag_class_to_dict)
register_dict_to_class("core.tag_controller.Tag", tag_dict_to_class)

threadPlayer = threading.Thread(target=playerUpdate)
threadPlayer.daemon = True
threadPlayer.start()

#print(yaMusic.getPlaylists())

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
