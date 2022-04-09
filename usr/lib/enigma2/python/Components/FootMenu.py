from Components.GUIComponent import GUIComponent
from Components.MultiContent import MultiContentEntryText , MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, eListbox, ePixmap, eLabel, eSize, ePoint, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO, BT_ALIGN_CENTER
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from skin import parseColor
import math

from sys import version_info

PY3 = version_info[0] == 3

class FlexibleMenu(GUIComponent):

	def __init__(self, list):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.list = list
		self.entries = dict()
		self.onSelectionChanged = []
		self.current = 0
		self.currentPage = 1
		self.total_pages = 1
		self.itemPerPage = 7
		self.columns = self.itemPerPage // 2
		self.margin = 5
		self.boxwidth = 240
		self.boxheight = 250
		self.activeboxwidth = 290
		self.activeboxheight = 295
		self.panelheight = 500
		self.ptr_pagerleft = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/icon/pager_left.png"))
		self.ptr_pagerright = LoadPixmap(resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/icon/pager_right.png"))
		self.itemPixmap = None
		self.selPixmap = None
		self.listWidth = 0
		self.listHeight = 0
		if PY3:
			import html
			self.selectedicon = str(html.unescape("&#xe837;"))
			self.unselectedicon = str(html.unescape("&#xe836;"))
		else:
			import HTMLParser
			h = HTMLParser.HTMLParser()
			self.selectedicon = str(h.unescape("&#xe837;"))
			self.unselectedicon = str(h.unescape("&#xe836;"))

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value) in self.skinAttributes:
			if attrib == "itemPerPage":
				self.itemPerPage = int(value)
				self.columns = int(value) // 2
			elif attrib == "panelheight":
				self.panelheight = int(value)
			elif attrib == "margin":
				self.margin = int(value)
			elif attrib == "boxSize":
				if value.find(',') == -1:
					self.boxwidth = int(value)
					self.boxheight = int(value)
				else:
					self.boxwidth = int(str(value).split(",")[0])
					self.boxheight = int(str(value).split(",")[1])
			elif attrib == "activeSize":
				if value.find(',') == -1:
					self.activeboxwidth = int(value)
					self.activeboxheight = int(value)
				else:
					self.activeboxwidth = int(str(value).split(",")[0])
					self.activeboxheight = int(str(value).split(",")[1])
			elif attrib == "size":
				self.listWidth = int(str(value).split(",")[0])
				self.listHeight = int(str(value).split(",")[1])
				if self.instance:
					self.instance.resize(eSize(self.listWidth, self.listHeight))
			elif attrib == "itemPixmap":
				self.itemPixmap = LoadPixmap(value)
			elif attrib == "selPixmap":
				self.selPixmap = LoadPixmap(value)
			else:
				attribs.append((attrib, value))
		self.l.setFont(0, gFont("FootFont", 23))
		self.l.setItemHeight(self.panelheight)

		self.pagelabel.setFont(gFont("FootIcons", 18))
		self.pagelabel.setVAlign(eLabel.alignCenter)
		self.pagelabel.setHAlign(eLabel.alignCenter)
		self.pagelabel.setBackgroundColor(parseColor("#FF272727"))
		self.pagelabel.setTransparent(1)
		self.pagelabel.setZPosition(100)
		self.pagelabel.move(ePoint(0, self.panelheight - 10))
		self.pagelabel.resize(eSize(1660, 20))
		self.pager_center.setBackgroundColor(parseColor("#00272727"))
		self.pager_left.resize(eSize(20,20))
		self.pager_right.resize(eSize(20, 20))
		self.pager_left.setPixmap(self.ptr_pagerleft)
		self.pager_right.setPixmap(self.ptr_pagerright)
		self.pager_left.setScale(2)
		self.pager_right.setScale(2)
		self.pager_left.setAlphatest(2)
		self.pager_right.setAlphatest(2)
		self.pager_left.hide()
		self.pager_right.hide()
		self.pager_center.hide()

		self.skinAttributes = attribs
		self.buildEntry()
		return GUIComponent.applySkin(self, desktop, parent)

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		self.instance = instance
		instance.setContent(self.l)
		instance.setSelectionEnable(0)
		instance.setScrollbarMode(eListbox.showNever)
		self.pager_left = ePixmap(self.instance)
		self.pager_center = eLabel(self.instance)
		self.pager_right = ePixmap(self.instance)
		self.pagelabel = eLabel(self.instance)
		
	def preWidgetRemove(self, instance):
		instance.setContent(None)
		self.instance = None

	def selectionChanged(self):
		for f in self.onSelectionChanged:
			f()

	def setList(self,list):
		self.list = list
		if self.instance:
			self.setL(True)

	def buildEntry(self):
		if len(self.list)> 0:
			width = self.boxwidth + self.margin
			height = self.boxheight + self.margin
			xoffset = ((self.activeboxwidth - self.boxwidth) // 2) if self.activeboxwidth > self.boxwidth else 0
			yoffset = ((self.activeboxheight - self.boxheight) // 2) if self.activeboxheight > self.boxheight else 0
			x = 0
			y = 0
			count = 0
			page = 1
			list_dummy = []
			self.total_pages = int(math.ceil(float(len(self.list))/self.itemPerPage))
			for elem in self.list:
				if count > self.itemPerPage-1:
					count = 0
					page += 1
					y = 0
				logo = None
				logoPath = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/compet/icons/{}.png".format(elem[0]))
				if fileExists(logoPath):
					logo = LoadPixmap(logoPath)
				self.entries.update({
					elem[0]:{
						"active":(
							MultiContentEntryPixmap(pos=(x, y), size=(self.activeboxwidth,self.activeboxheight), png=self.selPixmap, flags=BT_SCALE),
							MultiContentEntryPixmapAlphaTest(pos=(x, y), size=(self.activeboxwidth,self.activeboxheight), png=logo, flags=BT_SCALE|BT_ALIGN_CENTER|BT_KEEP_ASPECT_RATIO),
							MultiContentEntryText(pos=(x+57, y+168), size=(self.activeboxwidth, 34), font=0, text="Match" if elem[0] == "today" else ""),
							MultiContentEntryText(pos=(x+170, y+168), size=(self.activeboxwidth, 34), font=0, text="Today" if elem[0] == "today" else ""),
						),
						"u_active":(
							MultiContentEntryPixmap(pos=(x+xoffset, y+yoffset), size=(self.boxwidth,self.boxheight), png=self.itemPixmap, flags=BT_SCALE),
							MultiContentEntryPixmapAlphaTest(pos=(x+xoffset, y+yoffset), size=(self.boxwidth,self.boxheight), png=logo, flags=BT_SCALE|BT_ALIGN_CENTER|BT_KEEP_ASPECT_RATIO),
							MultiContentEntryText(pos=(x+60, y+160), size=(self.boxwidth, 34), font=0, text="Match" if elem[0] == "today" else ""),
							MultiContentEntryText(pos=(x+170, y+160), size=(self.boxwidth, 34), font=0, text="Today" if elem[0] == "today" else ""),
						),
						"page":page
					}
				})
				x += width
				list_dummy.append(elem[0])
				if len(list_dummy) == self.columns:
					list_dummy[:] = []
					x = 0
					y += height
				count += 1
			self.setL()

	def setL(self,refresh=False):
		if refresh:
			self.entries.clear()
			self.buildEntry()
			return
		if len(self.entries) > 0 and len(self.list) > 0:
			res = [None]
			try:
				current = self.entries[self.list[self.current][0]]
			except IndexError:
				self.current -= 1
				current = self.entries[self.list[self.current][0]]
			current_page = current['page']
			for _, value in self.entries.items():
				if current_page == value['page'] and value != current:
					res.append(value['u_active'][0])
					res.append(value['u_active'][1])
					res.append(value['u_active'][2])
					res.append(value['u_active'][3])
			res.append(current['active'][0])
			res.append(current['active'][1])
			res.append(current['active'][2])
			res.append(current['active'][3])
			self.l.setList([res])
			self.setpage()

	def setpage(self):
		if self.total_pages > 1:
			self.pagetext = ""
			if len(self.list) > 0:
				for i in range(1, self.total_pages+1):
					if self.getCurrentPage() > 0 and i == self.getCurrentPage():
						self.pagetext += " " + self.selectedicon
					else:
						self.pagetext += " " + self.unselectedicon
				self.pagetext += " "
			self.pagelabel.setText(self.pagetext)
			w = int(self.pagelabel.calculateSize().width() / 2)
			if self.total_pages > 1:
				x1 = (self.listWidth // 2) - w + 19
				x2 = (self.listWidth // 2) + (w-16)
				y = self.panelheight - 10
				self.pager_center.resize(eSize(x2-x1, 20))
				self.pager_center.move(ePoint(x2-x1, y))
				self.pager_center.move(ePoint((self.listWidth // 2)-w+20, y))
				self.pager_left.move(ePoint((self.listWidth // 2)-w, y))
				self.pager_right.move(ePoint((self.listWidth // 2) + (w-16), y))
				self.pager_left.show()
				self.pager_right.show()
				self.pager_center.show()
				self.pagelabel.show()
			else:
				self.pager_left.hide()
				self.pager_right.hide()
				self.pager_center.hide()
				self.pagelabel.hide()

	def getCurrentPage(self):
		if len(self.entries) > 0 and len(self.list) >0:
			try:
				current = self.entries[self.list[self.current][0]]
			except IndexError:
				self.current -= 1
				current = self.entries[self.list[self.current][0]]
			return current['page']
		else:
			return 0

	def left(self):
		self.move(1, 'backwards')
		
	def right(self):
		self.move(1, 'forward')
		
	def up(self):
		self.move(self.columns,'backwards')
		
	def down(self):
		if len(self.list) > 0:
			if self.current+self.columns > (len(self.list) -1) and self.current != (len(self.list) -1):
				self.current = len(self.list)-1
				self.setL()
				self.selectionChanged()
			else:
				self.move(self.columns,'forward')
	
	def move(self, step, direction):
		if len(self.list) > 0:
			if direction == 'backwards':
				self.current -= step
			else:
				self.current += step
			if self.current > (len(self.list)-1):
				self.current = 0
			if self.current < 0:
				self.current = len(self.list)-1
			self.setL()
			self.selectionChanged()

	def getCurrent(self):
		if len(self.list) >0:
			return self.list[self.current]
	
	def getSelectedIndex(self):
		return self.current
	
	def setIndex(self , index):
		self.current = index
		if self.instance:
			self.setL()
