# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.Label import Label 
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from enigma import eTimer, gRGB, loadPNG, gPixmapPtr, RT_WRAP, ePoint, RT_HALIGN_RIGHT, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, eConsoleAppContainer
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Plugins.Extensions.FootOnSat.ui.interface import FootOnSat, isHD, readFromFile
from xml.etree import ElementTree as ET


class FootOnsatLauncher(Screen):

	def __init__(self, session, *args):
		self.session = session
		Screen.__init__(self, session)
		skin = "assets/skin/HD/launcher.xml" if isHD() else "assets/skin/FHD/launcher.xml"
		self.skin = readFromFile(skin)
		self["setupActions"] = ActionMap(["FootOnsatActions"],
		{'left': self.left,
			'right': self.right,
			'up': self.up,
			'down': self.down,
			'ok':self.ok,
			"cancel": self.exit
		}, -1)
		self.menu = []
		skin_parsed = ET.fromstring(self.skin)
		for child in skin_parsed:
			if not child.get('name') == None:
				if '_off' in child.get('name') or '_on' in child.get('name'):
					self[child.get('name')] = Pixmap()
					compet = child.get('name').replace('_off','').replace('_on','')
					self.menu.append(compet) if compet not in self.menu else self.menu
		self['menu'] = MenuList([])
		self['menu'].l.setList(self.menu)
		self.Moveframe()

	def Moveframe(self):
		index = self['menu'].getSelectionIndex()
		tag = self.menu[index]
		for item in self.menu:
			if item == tag:
				self[item + '_on'].show()
				self[item + '_off'].hide()
			else:
				self[item + '_off'].show()
				self[item + '_on'].hide()

	def ok(self):
		index = self['menu'].getSelectionIndex()
		compet = self.menu[index]
		self.session.open(FootOnSat,compet)
				
	def left(self):
		self['menu'].up()
		self.Moveframe()

	def right(self):
		self['menu'].down()
		self.Moveframe()

	def up(self):
		self['menu'].up()
		self.Moveframe()

	def down(self):
		self['menu'].down()
		self.Moveframe()

	def exit(self):
		self.close()
