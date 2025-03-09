EN_LOCALE = {
	"player.name": "Kitsune"
}

class LocaleConfig:
	def __init__(self, config):
		#TODO: read from config
		self.locale = EN_LOCALE

	def getText(self, id: str) -> str:
		return self.locale.get(id, id)
