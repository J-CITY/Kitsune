import os
class LocaleConfig:
	def __init__(self, config):
		self.locale = {}
		if os.path.exists(config.locale):
			import json
			data = None
			with open(config.locale) as f:
				data = json.load(f)
			for k, v in data.items():
				self.locale[k] = v

	def getText(self, id: str) -> str:
		return self.locale.get(id, id)
