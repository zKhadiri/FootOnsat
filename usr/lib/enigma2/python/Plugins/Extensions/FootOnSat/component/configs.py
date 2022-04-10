from Components.config import ConfigElement

class ConfigDictionarySet(ConfigElement):
	def __init__(self, default={}):
		ConfigElement.__init__(self)
		self.default = default
		self.dirs = {}
		self.value = self.default
		self.callback = None

	def load(self):
		# self.dirs = self.default if self.saved_value is None else self.fromString(self.saved_value)
		ConfigElement.load(self)
		self.dirs = self.value

	def save(self):
		del_keys = []
		for key in self.dirs:
			if not len(self.dirs[key]):
				del_keys.append(key)
		for del_key in del_keys:
			try:
				del self.dirs[del_key]
			except KeyError:
				pass
			self.changed()
			if callable(self.callback):
				self.callback()
		self.saved_value = self.toString(self.dirs)

	def handleKey(self, key, callback=None):
		self.callback = callback

	def fromString(self, val):
		return eval(val)

	def toString(self, value):
		return str(value)

	def getValue(self):
		return self.dirs

	def setValue(self, value):
		if isinstance(value, dict):
			prev = self.dirs
			self.dirs = value
			if self.dirs != prev:
				self.changed()
				if callable(self.callback):
					self.callback()

	value = property(getValue, setValue)

	def getConfigValue(self, value, config_key):
		if isinstance(value, str) and isinstance(config_key, str):
			if value in self.dirs and config_key in self.dirs[value]:
				return self.dirs[value][config_key]
		return None

	def changeConfigValue(self, value, config_key, config_value):
		if isinstance(value, str) and isinstance(config_key, str):
			if value in self.dirs:
				self.dirs[value][config_key] = config_value
			else:
				self.dirs[value] = {config_key: config_value}
			self.changed()
			if callable(self.callback):
				self.callback()

	def removeConfigValue(self, value, config_key):
		if isinstance(value, str) and isinstance(config_key, str) and value in self.dirs and config_key in self.dirs[value]:
			del self.dirs[value][config_key]
			self.changed()
			if callable(self.callback):
				self.callback()

	def getKeys(self):
		return self.dir_pathes