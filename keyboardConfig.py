from enum import Enum
from typing import Dict, List

class EKeyAction(Enum):
	FRAME_MAIN_PLAYLIST_ACTIVE = 1
	FRAME_PLAYLISTS_ACTIVE = 2
	FRAME_VIZUALIZER_ACTIVE = 3
	FRAME_LYRICS_ACTIVE = 4
	FRAME_ARTIST_INFO_ACTIVE = 5

class KeyboardConfig:
	def __init__(self, config):
		self.keyMap: Dict[EKeyAction, List[int]] = {}
		#TODO : read config

	def getKey(self, id: EKeyAction) -> List[int]:
		if (id in self.keyMap):
			return self.keyMap[id]
		return []
