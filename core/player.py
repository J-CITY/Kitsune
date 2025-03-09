import os, sys
parentPath = os.path.abspath("../")
if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from pybass.pybass import *
from core.utils import log, LogLevel
import time
from random import randint
from core.tag_controller import *
from multiprocessing import Process
from core.strings import OS_LINUX, OS_WIN

class PlayMode:
	MOD_ONE_SONG = 0
	MOD_SONG_CIRCLE = 1
	MOD_ONE_PLAYLIST = 2
	MOD_PLAYLIST_CIRCLE = 3
	MOD_PLAYLIST_RANDOM = 4

BASS_ATTRIB_TEMPO = 0x10000
BASS_FX_FREESOURCE = 0x10000

class Player:
	def __init__(self, config):
		# load dll/so
		if platform.system() == OS_LINUX:
			self.fx_module  = ctypes.cdll.LoadLibrary("libc.so.6")
			self.fx_func_type = ctypes.CFUNCTYPE
			self.BASS_FX_TempoCreate = func_type(HSTREAM, ctypes.c_ulong, ctypes.c_ulong)(('BASS_FX_TempoCreate', self.fx_module))
		elif platform.system() == OS_WIN:
			self.fx_module = ctypes.WinDLL('./bass_fx.dll')
			self.fx_func_type = ctypes.WINFUNCTYPE
			self.BASS_FX_TempoCreate = func_type(HSTREAM, ctypes.c_ulong, ctypes.c_ulong)(('BASS_FX_TempoCreate', self.fx_module))

		# Init BASS lib
		if not BASS_Init(-1, 44100, 0, 0, 0):
			log(LogLevel.ERROR, "BASSlib can not init", get_error_description(BASS_ErrorGetCode()))
			sys.exit(1)

		# init streams
		self.streams = [BASS_StreamCreateFile(False, "", 0, 0, BASS_UNICODE), BASS_StreamCreateFile(False, "", 0, 0, BASS_UNICODE)]
		self.streamsId = 0

		# load cache playlist
		path = os.path.join(config.cache_folder, "cache.json")
		self.playlist = loadPlaylist(path)

		# TODO: save to cache id, mode, crossfate, and add def values to config
		self.playlistId = 0
		self.isPlay = False
		self.mode = 0
		self.crossfade = False
		self.cfParam = 5 # crossfade offset, TODO: add to config
		self.volume = BASS_GetVolume()

		#EQ
		self.EQGainBassSize = 3
		self.EQGainBass = [6, 5, 4]

		self.EchoHandle = 0
		self.EchoParam = BASS_DX8_ECHO()
		self.EchoParam.fWetDryMix = 0
		self.EchoParam.fFeedback = 0
		self.EchoParam.fLeftDelay = 333
		self.EchoParam.fRightDelay = 333
		self.EchoParam.lPanDelay = False
		self.isEcho = False

		self.ChorusHandle = 0
		self.ChorusParam = BASS_DX8_CHORUS()
		self.ChorusParam.fWetDryMix = 0
		self.ChorusParam.fDepth = 25
		self.ChorusParam.fFeedback = 0
		self.ChorusParam.fFrequency = 0
		self.ChorusParam.lWaveform = 1
		self.ChorusParam.fDelay = 0
		self.ChorusParam.lPhase = 0
		self.isChorus = False

		self.ReverbHandle = 0
		self.ReverbParam = BASS_DX8_REVERB()
		self.ReverbParam.fInGain = 0
		self.ReverbParam.fReverbMix = 0
		self.ReverbParam.fReverbTime = 1000
		self.ReverbParam.fHighFreqRTRatio = 0.001
		self.isReverb = False

		self.FlangeHandle = 0
		self.FlangeParam = BASS_DX8_FLANGER()
		self.FlangeParam.fWetDryMix = 0
		self.FlangeParam.fDepth = 25
		self.FlangeParam.fFeedback = 0
		self.FlangeParam.fFrequency = 0
		self.FlangeParam.lWaveform = 1
		self.FlangeParam.fDelay = 0
		self.FlangeParam.lPhase = 0
		self.isFlange = False

		self.levelCount = 10
		self.EQCenter = [80, 170, 310, 600, 1000, 3000, 6000, 10000, 12000, 14000]
		self.EQHandle = [0,0,0,0,0,0,0,0,0,0]
		self.isBass = False
		self.eqLevelParam = [0, 0, 0 ,0, 0, 0, 0, 0, 0, 0]
		self.eqSpeedParam = 0

		self.updatePlayerItemCb = None
		self.getYandexMusicUrlCb = None

		#Visualization
		# TODO: add to confit def param and to cache
		# self.param = config.visualization

	#def __del__(self):
	#	self.destructor()
	#TODO: delete it
	def setUpdatePlayerItemCb(self, cb):
		self.updatePlayerItemCb = cb

	def setGetYandexMusicUrlCb(self, cb):
		self.getYandexMusicUrlCb = cb

	def getTag(self) -> Tag|None:
		if (len(self.playlist.tracks) > self.playlistId):
			return self.playlist.tracks[self.playlistId]
		else:
			return None

	def destructor(self):
		for s in self.streams:
			BASS_StreamFree(s)
		BASS_Free()

	def playOnline(self):
		if self.getYandexMusicUrlCb:
			trackUrl = self.getYandexMusicUrlCb(self.playlist.tracks[self.playlistId].globalId)
		#print(trackUrl)
		if trackUrl is not None:
			fxch = BASS_StreamCreateURL(trackUrl.encode("utf-8"), False, BASS_STREAM_DECODE, DOWNLOADPROC(), 0)
			self.streams[self.streamsId] = self.BASS_FX_TempoCreate(fxch, BASS_FX_FREESOURCE)

	def play(self):
		print("play")
		self.isPlay = True
		#BASS_ChannelStop(self.streams[self.streamsId])
		
		self.streamsId = (self.streamsId + 1) % 2
		_url = ''
		if len(self.playlist.tracks) > self.playlistId:
			track = self.playlist.tracks[self.playlistId]
			_url = track.url

		#BASS_ChannelStop(self.streams[self.streamsId])
		#BASS_StreamFree
		if _url.startswith('http') or _url.startswith('ftp'):
			# Now this case is impossible, because we can`t add it to playlist. But maybe in feature :thinking:
			fxch = BASS_StreamCreateURL(_url.encode("utf-8"), False, BASS_STREAM_DECODE, DOWNLOADPROC(), 0)
			self.streams[self.streamsId] = self.BASS_FX_TempoCreate(fxch, BASS_FX_FREESOURCE)
		elif track.type == TrackType.YANDEX_MUSIC:
			self.playOnline()
		else:
			fxch = BASS_StreamCreateFile(False, _url, 0, 0, BASS_UNICODE|BASS_STREAM_DECODE)
			self.streams[self.streamsId] = self.BASS_FX_TempoCreate(fxch, BASS_FX_FREESOURCE)
		#log(LogLevel.Info, _url.encode("utf-8"))
		BASS_ChannelPlay(self.streams[self.streamsId], False)
		
		self.setEqParams()
		#print("play1")
		#if self.updatePlayerItemCb is not None:
		#	print(self.playlistId)
		#	tag = self.playlist.tracks[self.playlistId]
		#	tag.length = self.getLen()
		#	print("call1")
		#	self.updatePlayerItemCb._pyroClaimOwnership()
		#	print("call2")
		#	self.updatePlayerItemCb.updatePlayerItemCb(self.playlistId, tag)
		#else:
		#	print("NONE")

	def stop(self):
		self.isPlay = False
		BASS_ChannelStop(self.streams[0])
		BASS_ChannelStop(self.streams[1])

	def next(self):
		#TODO: add loop
		self.isPlay = True
		if self.playlistId < self.playlist.getSize() - 1:
			self.playlistId += 1
			self.play()

	def prev(self):
		# TODO: add loop
		self.isPlay = True
		if (self.playlistId > 0):
			self.playlistId -= 1
			self.play()

	def getVolume(self):
		return BASS_GetVolume()

	def getVolumeInPercent(self):
		return BASS_GetVolume() * 100

	def setVolume(self, _volume):
		self.volume = 1 if _volume > 1 else _volume
		self.volume = 0 if _volume < 0 else _volume
		BASS_SetVolume(self.volume)

	def offOnVolume(self):
		#TODO: save prev volume
		v = 0
		if BASS_GetVolume() == 0:
			v = 0.5 if self.volume == 0 else self.volume
		BASS_SetVolume(v)

	def pause(self):
		if BASS_ChannelIsActive(self.streams[self.streamsId]) == BASS_ACTIVE_PLAYING:
			BASS_ChannelPause(self.streams[self.streamsId])
			self.isPlay = False
		else:
			if self.streams[self.streamsId] == 0:
				self.playlistId = 0
				#self.presenter.mainPlaylistSetPlayId(0)
				#tag = self.playlist.tracks[0]
				#tag.length = self.getLen()
				#self.presenter.song = tag
				self.play()
			else:
				print("play 2")
				BASS_ChannelPlay(self.streams[self.streamsId], False)
			self.isPlay = True
		
	def move(self, mov):
		len = BASS_ChannelGetLength(self.streams[self.streamsId], BASS_POS_BYTE)
		buf = BASS_ChannelGetPosition(self.streams[self.streamsId], BASS_POS_BYTE)
		slen = BASS_ChannelBytes2Seconds(self.streams[self.streamsId], len)
		sbuf = BASS_ChannelBytes2Seconds(self.streams[self.streamsId], buf)
		sbuf += mov
		if (sbuf < 0):
			sbuf = 0
		if (sbuf > slen):
			sbuf = slen
		buf = BASS_ChannelSeconds2Bytes(self.streams[self.streamsId], sbuf)
		BASS_ChannelSetPosition(self.streams[self.streamsId], buf, BASS_POS_BYTE)

	def getLen(self):
		if self.streams[self.streamsId] == 0:
			return 0
		_len = BASS_ChannelGetLength(self.streams[self.streamsId], BASS_POS_BYTE)
		slen = BASS_ChannelBytes2Seconds(self.streams[self.streamsId], _len)
		return slen

	def getBuf(self):
		if self.streams[self.streamsId] == 0:
			return 0
		buf = BASS_ChannelGetPosition(self.streams[self.streamsId], BASS_POS_BYTE)
		sbuf = BASS_ChannelBytes2Seconds(self.streams[self.streamsId], buf)
		return sbuf

	def getIsPlay(self):
		return self.isPlay
		#if self.streams[self.streamsId] == 0:
		#	return False
		#else:
		#	return True

	#def setPresenter(self, p):
	#	self.presenter = p
	#	if self.playlist.tracks != []:
	#		self.presenter.mainPlaylistUpdateList()

	def update(self):
		while True:
			if self.mode == PlayMode.MOD_ONE_SONG:
				time.sleep(.200)
				continue

			canPlay = 0.0
			if self.crossfade:
				canPlay = self.cfParam

			if self.isPlay:
				_len = BASS_ChannelGetLength(self.streams[self.streamsId], BASS_POS_BYTE)
				_buf = BASS_ChannelGetPosition(self.streams[self.streamsId], BASS_POS_BYTE)
				_slen = BASS_ChannelBytes2Seconds(self.streams[self.streamsId], _len)
				_sbuf = BASS_ChannelBytes2Seconds(self.streams[self.streamsId], _buf)
				if _slen - _sbuf <= canPlay:
					lenPl = len(self.playlist.tracks)
					if self.mode == PlayMode.MOD_PLAYLIST_CIRCLE and lenPl > 0:
						self.playlistId += 1
						if self.playlistId >= lenPl:
							self.playlistId = 0
					if self.mode == PlayMode.MOD_ONE_PLAYLIST and lenPl > 0:
						self.playlistId += 1
						if self.playlistId >= lenPl:
							self.stop()
							time.sleep(.200)
							continue
					elif self.mode == PlayMode.MOD_PLAYLIST_RANDOM and lenPl > 0:
						self.playlistId = randint(0, lenPl-1)
					elif self.mode == PlayMode.MOD_SONG_CIRCLE:
						pass
					elif lenPl == 0:
						self.stop()
						time.sleep(.200)
						continue

					self.play()
					#self.presenter.mainPlaylistUpdatePlayItem()
			time.sleep(.200)

	def setEqLevelParam(self, param):
		self.eqLevelParam = param
	def setEqSpeedParam(self, param):
		self.eqSpeedParam = param
		#BASS_ChannelPlay(tempostream, False)
	def setEqBass(self, param):
		self.isBass = param
	def setEqEcho(self, param):
		self.isEcho = param
	def setEqFlange(self, param):
		self.isFlange = param
	def setEqChorus(self, param):
		self.isChorus = param
	def setEqReverb(self, param):
		self.isReverb = param

	def restoreSoundEffect(self):
		for i in range(0, self.levelCount):
			if BASS_ChannelRemoveFX(self.streams[self.streamsId], self.EQHandle[i]):
				self.EQHandle[i] = 0
				
		if self.EchoHandle != 0 and BASS_ChannelRemoveFX(self.streams[self.streamsId], self.EchoHandle):
			self.EchoHandle = 0
		if self.ChorusHandle != 0 and BASS_ChannelRemoveFX(self.streams[self.streamsId], self.ChorusHandle):
			self.ChorusHandle = 0
		if self.ReverbHandle != 0 and BASS_ChannelRemoveFX(self.streams[self.streamsId], self.ReverbHandle):
			self.ReverbHandle = 0
		if self.isFlange != 0 and BASS_ChannelRemoveFX(self.streams[self.streamsId], self.isFlange):
			self.isFlange = 0

	def setEqParams(self):
		self.restoreSoundEffect()
		#self.EQHandle = []
		for i in range(0, self.levelCount):
			#if EQHandle[i] == 0:
			self.EQHandle[i] = BASS_ChannelSetFX(self.streams[self.streamsId], BASS_FX_DX8_PARAMEQ, 1)
			#}
			EQParam = BASS_DX8_PARAMEQ()
			EQParam.fCenter = self.EQCenter[i]
			EQParam.fBandwidth = 3
			#if i < (levelCount-1):
			if self.isBass and i < self.EQGainBassSize:
				EQParam.fGain = self.EQGainBass[i]
			else:
				EQParam.fGain = self.eqLevelParam[i]
			
			if BASS_FXSetParameters(self.EQHandle[i], ctypes.pointer(EQParam)) == 0:
				log(LogLevel.ERROR, 'setEqParams, error FX')

		if self.isChorus:
			if self.ChorusHandle == 0:
				self.ChorusHandle = BASS_ChannelSetFX(self.streams[self.streamsId], BASS_FX_DX8_CHORUS, 1)
			if self.ChorusHandle != 0:
				if BASS_FXGetParameters(self.ChorusHandle, ctypes.pointer(self.ChorusParam)):
					BASS_FXSetParameters(self.ChorusHandle, ctypes.pointer(self.ChorusParam))

		if self.isEcho:
			if self.EchoHandle == 0:
				self.EchoHandle = BASS_ChannelSetFX(self.streams[self.streamsId], BASS_FX_DX8_ECHO, 1)
			if self.EchoHandle != 0:
				if BASS_FXGetParameters(self.EchoHandle, ctypes.pointer(self.EchoParam)):
					BASS_FXSetParameters(self.EchoHandle, ctypes.pointer(self.EchoParam))

		if self.isReverb:
			if self.ReverbHandle == 0:
				self.ReverbHandle = BASS_ChannelSetFX(self.streams[self.streamsId], BASS_FX_DX8_REVERB, 1)
			if self.ReverbHandle != 0:
				if BASS_FXGetParameters(self.ReverbHandle, ctypes.pointer(self.ReverbParam)):
					BASS_FXSetParameters(self.ReverbHandle, ctypes.pointer(self.ReverbParam))

		if self.isFlange:
			if self.FlangeHandle == 0:
				self.FlangeHandle = BASS_ChannelSetFX(self.streams[self.streamsId], BASS_FX_DX8_FLANGER, 1)
			if self.FlangeHandle != 0:
				if BASS_FXGetParameters(self.FlangeHandle, ctypes.pointer(self.FlangeParam)):
					BASS_FXSetParameters(self.FlangeHandle, ctypes.pointer(self.FlangeParam))

		BASS_ChannelSetAttribute(self.streams[self.streamsId], BASS_ATTRIB_TEMPO, self.eqSpeedParam)

	def getWaveData(self, isStereo, col):
		ci = BASS_CHANNELINFO()
		if not BASS_ChannelGetInfo(self.streams[self.streamsId], ci):
			print(('BASS_ChannelGetInfo error', get_error_description(BASS_ErrorGetCode())))
			return
		channel = ci.chans if isStereo else 1
		buf = (ctypes.c_float*(channel * col * 4))()#[channel * col * 4]
		BASS_ChannelGetData(self.streams[self.streamsId], buf, (ci.chans * col * 4) | BASS_DATA_FLOAT)

		return {
			"data": buf,
			"channel": channel
		}

	def getFFTData(self, isStereo):
		fft = (ctypes.c_float*1024)()
		BASS_ChannelGetData(self.streams[self.streamsId], fft, BASS_DATA_FFT2048)
		return {
			"data": fft,
			"channel": 2 if isStereo else 1
		}


