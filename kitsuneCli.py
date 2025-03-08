from core.utils import log, LogLevel
import time
import asyncio
try:
	from Pyro5.api import expose, callback, Daemon, Proxy
	import argparse
except ImportError or ModuleNotFoundError:
	log(LogLevel.ERROR, "Pyro5 lib not found")
	exit(1)

REQUEST_IS_DONE = False

def requestIdDone():
	global REQUEST_IS_DONE
	REQUEST_IS_DONE = True

class CallbackHandler(object):
	@expose
	@callback
	def callbackLyrics(self, str):
		requestIdDone()
		print("Lyrics:\n", str)

	@expose
	@callback
	def callbackArtistInfo(self, str):
		requestIdDone()
		print("Artist info:\n", str)

	@expose
	@callback
	def default(self):
		requestIdDone()

#import Pyro5.api
#
#name = input("What is your name? ").strip()
#
#greeting_maker = Pyro5.api.Proxy("PYRONAME:example.greeting")    # use name server object lookup uri shortcut
#print(greeting_maker.get_fortune(name))

def prepareArgs():
	parser = argparse.ArgumentParser()

	#parser.add_argument("-infMode", action="store_true", help="Do not close after command")
	#parser.set_defaults(infMode=False)

	parser.add_argument("-db", action="store_true", help="Update music database")
	parser.set_defaults(play=False)

	parser.add_argument("-play", action="store_true", help="Play")
	parser.set_defaults(play=False)

	parser.add_argument("-pause", action="store_true", help="Pause")
	parser.set_defaults(pause=False)

	parser.add_argument("-stop", action="store_true", help="Stop")
	parser.set_defaults(stop=False)

	parser.add_argument("-prev", action="store_true", help="Prev")
	parser.set_defaults(prev=False)

	parser.add_argument("-next", action="store_true", help="Next")
	parser.set_defaults(next=False)

	parser.add_argument("-volUp", action="store_true", help="volUp")
	parser.set_defaults(volUp=False)

	parser.add_argument("-volDown", action="store_true", help="volDown")
	parser.set_defaults(volDown=False)

	parser.add_argument("-volGet", action="store_true", help="volGet")
	parser.set_defaults(volDown=False)

	parser.add_argument("-volSet", type=int, help="Set volume")

	parser.add_argument("-mute", action="store_true", help="mute")
	parser.set_defaults(mute=False)

	parser.add_argument("-current", action="store_true", help="get current song info")
	parser.set_defaults(current=False)

	parser.add_argument("-curpl", action="store_true", help="get current playlist")
	parser.set_defaults(curpl=False)

	parser.add_argument("-lyrics", action="store_true", help="get lyrics")
	parser.set_defaults(lyrics=False)

	parser.add_argument("-artist_info", action="store_true", help="get artist info")
	parser.set_defaults(artist_info=False)

	parser.add_argument("-add", type=str, help="Add song")

	return parser.parse_args()

def runCommand(server, callback, args):
	global REQUEST_IS_DONE
	if args.db:
		server.updateDb(callback)
		return
	elif args.play:
		server.play()
	elif args.pause:
		server.pause()
	elif args.stop:
		server.stop()
	elif args.prev:
		server.prev()
	elif args.next:
		server.next()
	elif args.volUp:
		server.volumeUp()
	elif args.volDown:
		server.volumeDown()
	elif args.volGet:
		volume = server.getVolume()
	elif args.volSet is not None:
		server.setVolume(args.volSet)
	elif args.current:
		tag = server.getCurrentSong()
	elif args.mute:
		server.mute()
	elif args.add is not None:
		server.add(args.add)
	elif args.curpl:
		pl = server.getCurrentPlaylist()

	elif args.lyrics:
		server.getLyrics(callback)
	elif args.artist_info:
		server.getArtistInfo(callback)

	REQUEST_IS_DONE = True

def main():
	# init daemon and callback
	daemon = Daemon()
	callback = CallbackHandler()
	daemon.register(callback)

	server = Proxy("PYRONAME:kitsune.music.daemon")

	# argparse
	args = prepareArgs()
	
	runCommand(server, callback, args)
	#server.getLirics(callback_handler)
	#print(server.getCurrentSong())

	# wait request
	#daemon.requestLoop()
	daemon.requestLoop(loopCondition=lambda: REQUEST_IS_DONE == False)

if __name__ == "__main__":
	main()
