from pybass import *
BASS_Init(-1, 44100, 0, 0, 0)
#filePlayerHandle = BASS_StreamCreateURL("http://cdndl.zaycev.net/265742/1724020/imagine_dragons_-_demons_%28zaycev.net%29.mp3".encode("utf-8"), False, 0,DOWNLOADPROC(),0)
import time
import soundcloud

client = soundcloud.Client(client_id='W0ZdiZBIDSyAgLzanrI8txpEP8ne1OPC',
                           client_secret='ljzN66hCvr4e6JzPJ3K4HXVkMdOLEPy6',
                           username='333danich333@gmail.com',
                           password='db4kq5b210B')


print(client.get('/me').username)
likes = client.get('/me/favorites')
#for t in likes:
#	print(t.title, ' ', t.id)
track = likes[0]
stream_url = client.get(track.stream_url, allow_redirects=False)

#filePlayerHandle = BASS_StreamCreateURL(stream_url.location.encode("utf-8"), False, 0,DOWNLOADPROC(),0)



filePlayerHandle = BASS_StreamCreateFile(False, "", 0, 0, BASS_UNICODE)
#BASS_ChannelPlay(filePlayerHandle, False)
#BASS_ChannelPlay(filePlayerHandle, False)
#while BASS_ChannelPlay(filePlayerHandle, False):
#	time.sleep(1)
#play_handle(filePlayerHandle, show_tags = False)
BASS_StreamFree(filePlayerHandle)
BASS_Free()