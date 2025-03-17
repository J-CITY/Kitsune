# Kitsune - music player daemon with text user interface client

![Screenshot](https://github.com/J-CITY/Kitsune/blob/daemon/screens/main1.png)

## Description
Powerful console music player written with Python.

### Features

- Make playlists
- Show artist bio
- Show song lyrics
- Play Yandex Music favorites and playlists
- Fully customization (See configs in `./assets`)
- Equalizer
- Local music library
- Music file browser
- Music visualization
- Clock

I think this should work on Linux, but I have not tested ¯\\_(ツ)_/¯


## Start daemon

### 1. Start pyro5 name server

```
python -m Pyro5.nameserver
```

### 2. Start daemon

```
python ./kitsuneDaemon.py
```

## Start client

```
python ./kitsunePlayer.py
```


# Dependencies (Python x64)

## Unnecessary

```
pip install asciimatics wcwidth six Pyro5 pybass numpy
```

## Necessary

```
pip install yandex-music pylast requests music_tag pillow term_image
```

## Create local media lib (Run after start daemon)

```
python ./kitsuneCli.py -db
```

## API keys

For artist bio and Yandex music you need get api kays

# Screenshots

Main playlist:

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/main0.png)
![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/main1.png)

Browser

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/browser.png)

Playlists

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/playlists.png)

Medialib

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/medialib.png)

Equalizer

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/eq.png)

Artist info

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/bio.png)

Lirycs

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/lyrics.png)

Clock

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/clock.png)

Visualization

![Imgur](https://github.com/J-CITY/Kitsune/blob/daemon/screens/viz.gif)
