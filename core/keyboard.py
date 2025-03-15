from enum import Enum
from typing import Dict, List
import os

class EKeyAction(Enum):
	PLAY_PAUSE = 0
	STOP = 1
	EXIT = 2
	INFO = 3

class Keyboard:
	def __init__(self, config):
		from asciimatics.screen import Screen
		self.keyMap: Dict[EKeyAction, List[int]] = {}
		data = None
		if os.path.exists(config.key_map):
			import json
			data = None
			with open(config.key_map) as f:
				data = json.load(f)
			for k, v in data.items():
				karr = []
				for key in v:
					cmd = key.split('|')
					if len(cmd) == 1:
						karr.append(ord(key))
					elif len(cmd) == 2:
						if cmd[0] == "Ctrl":
							karr.append(Screen.ctrl(cmd[1]))
				self.keyMap[EKeyAction[k]] = karr

	def getKey(self, id: EKeyAction) -> List[int]:
		return self.keyMap.get(id, [])
