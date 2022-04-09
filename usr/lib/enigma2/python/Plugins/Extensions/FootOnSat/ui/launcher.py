# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigDictionarySet, NoSave
from Plugins.Extensions.FootOnSat.ui.interface import FootOnSat, readFromFile
from Components.FootMenu import FlexibleMenu
from Plugins.Extensions.FootOnSat.__init__ import __version__
from twisted.web.client import getPage
import re
from sys import version_info

PY3 = version_info[0] == 3

config.plugins.FootOnSat = ConfigSubsection()
config.plugins.FootOnSat.sort = ConfigDictionarySet(default={"footmenu": {"footsubmenu": {}}})

class FootOnsatLauncher(Screen):

	def __init__(self, session, *args):
		self.session = session
		Screen.__init__(self, session)
		skin = "assets/skin/FHD/launcher.xml"
		self.skin = readFromFile(skin)
		self["setupActions"] = ActionMap(["FootOnsatActions"],
		{
			'left': self.left,
			'right': self.right,
			'up': self.up,
			'down': self.down,
			'ok': self.ok,
			'blue': self.keyBlue,
			'red': self.exit,
			"yellow": self.keyYellow,
			"cancel": self.exit
		}, -1)
		self['menu'] = FlexibleMenu([])
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["red"] = Label()
		self["red"].setText("V{}".format(__version__))
		self["green"] = Label()
		self["yellow"] = Label()
		self["blue"] = Label()
		self.menuList = []
		self.sort_mode = False
		self.selected_entry = None
		self.onLayoutFinish.append(self.callAPI)

	def callAPI(self):
		url = 'http://tunisia01.selfip.com/footonsat/api'
		getPage(str.encode(url)).addCallback(self.getData).addErrback(self.error)

	def getData(self, data):
		if PY3:
			data = data.decode('UTF-8')
		compet = re.findall(r'<a\s+href=\"(.*?).json\">', data)
		ordering = ["today", "championsleague", "europaleague", "ConferenceLeague", "premierleague", "laliga", "seriea",
		"bundesliga", "ligue1", "liganos","cafchampions", "afcchampions","championship", "laliga2", "nba"]
		self.menuList = self.custom_sort(ordering, compet)

		self.sub_menu_sort = NoSave(ConfigDictionarySet())
		self.sub_menu_sort.value = config.plugins.FootOnSat.sort.getConfigValue("footmenu", "footsubmenu") or {}
		idx = 0
		i = 10
		for _ in self.menuList:
			entry = [self.menuList.pop(idx)]
			m_weight = self.sub_menu_sort.getConfigValue("".join(entry), "sort") or i
			entry.append(m_weight)
			self.menuList.insert(idx, tuple(entry))
			self.sub_menu_sort.changeConfigValue(entry[0], "sort", m_weight)
			idx += 1
			i += 10
		self.full_list = list(self.menuList)
		self["blue"].setText("Edit mode on")
		self.hide_show_entries()
		self["menu"].setList(self.menuList)
		self.selectionChanged()

	def custom_sort(self, ordem_custom, origin):
		list_order_equals = [c for c in ordem_custom if (c in origin)]
		list_no_equals = [c for c in origin if (not c in ordem_custom)]
		list_order = list_order_equals + list_no_equals
		return list_order

	def error(self, error=None):
		if error:
			self.session.openWithCallback(self.exit, MessageBox, _('An Unexpected Error Occurred During The API Request !!'), MessageBox.TYPE_ERROR, timeout=10)

	def ok(self):
		if self.sort_mode and len(self.menuList):
			m_entry = self["menu"].getCurrent()[0]
			select = False
			if self.selected_entry is None:
				select = True
			elif self.selected_entry != m_entry:
				select = True
			if not select:
				self["green"].setText(_("Move mode on"))
				self.selected_entry = None
			else:
				self["green"].setText(_("Move mode off"))
			idx = 0
			for x in self.menuList:
				if m_entry == x[0] and select == True:
					self.selected_entry = m_entry
					break
				elif m_entry == x[0] and select == False:
					self.selected_entry = None
					break
				idx += 1
		elif len(self.menuList) and not self.sort_mode:
			compet = self['menu'].getCurrent()[0]
			self.session.open(FootOnSat, compet)

	def left(self):
		self.cur_idx = self["menu"].getSelectedIndex()
		self['menu'].left()
		if self.sort_mode and self.selected_entry is not None:
			self.moveAction()

	def right(self):
		self.cur_idx = self["menu"].getSelectedIndex()
		self['menu'].right()
		if self.sort_mode and self.selected_entry is not None:
			self.moveAction()

	def up(self):
		self.cur_idx = self["menu"].getSelectedIndex()
		self['menu'].up()
		if self.sort_mode and self.selected_entry is not None:
			self.moveAction()

	def down(self):
		self.cur_idx = self["menu"].getSelectedIndex()
		self['menu'].down()
		if self.sort_mode and self.selected_entry is not None:
			self.moveAction()

	def moveAction(self):
		if len(self.menuList) > 0:
			tmp_list = list(self.menuList)
			entry = tmp_list.pop(self.cur_idx)
			newpos = self["menu"].getSelectedIndex()
			tmp_list.insert(newpos, entry)
			self.menuList = list(tmp_list)
			self["menu"].setList(self.menuList)

	def selectionChanged(self):
		if self.sort_mode and len(self.menuList) > 0:
			selection = self["menu"].getCurrent()[0]
			if self.sub_menu_sort.getConfigValue(selection, "hidden"):
				self["yellow"].setText("show")
			else:
				self["yellow"].setText("hide")
		else:
			self["yellow"].setText("")

	def keyBlue(self):
		if len(self.menuList) > 0:
			self.toggleSortMode()

	def keyYellow(self):
		if self.sort_mode:
			m_entry = self["menu"].getCurrent()[0]
			hidden = self.sub_menu_sort.getConfigValue(m_entry, "hidden") or 0
			if hidden:
				self.sub_menu_sort.removeConfigValue(m_entry, "hidden")
				self["yellow"].setText(_("hide"))
			else:
				self.sub_menu_sort.changeConfigValue(m_entry, "hidden", 1)
				self["yellow"].setText(_("show"))

	def toggleSortMode(self):
		if self.sort_mode:
			self["green"].setText("")
			self["yellow"].setText("")
			self["blue"].setText(_("Edit mode on"))
			self.sort_mode = False
			i = 10
			idx = 0
			for x in self.menuList:
				self.sub_menu_sort.changeConfigValue(x[0], "sort", i)
				if len(x) >= 2:
					entry = list(x)
					entry[1] = i
					entry = tuple(entry)
					self.menuList.pop(idx)
					self.menuList.insert(idx, entry)
				if self.selected_entry is not None:
					if x == self.selected_entry:
						self.selected_entry = None
				i += 10
				idx += 1
			self.full_list = list(self.menuList)
			config.plugins.FootOnSat.sort.changeConfigValue("footmenu", "footsubmenu", self.sub_menu_sort.value)
			config.plugins.FootOnSat.sort.save()
			self.hide_show_entries()
			self["menu"].setList(self.menuList)
		else:
			self["green"].setText(_("Move mode on"))
			self["blue"].setText(_("Edit mode off"))
			self.sort_mode = True
			self.hide_show_entries()
			self["menu"].setList(self.menuList)
			self.selectionChanged()

	def hide_show_entries(self):
		m_list = list(self.full_list)
		if not self.sort_mode:
			rm_list = []
			for entry in m_list:
				if self.sub_menu_sort.getConfigValue(entry[0], "hidden"):
					rm_list.append(entry)
			for entry in rm_list:
				if entry in m_list:
					m_list.remove(entry)
		if not len(m_list):
			m_list.append((self.full_list[0][0], 10))
		m_list.sort(key=lambda listweight: int(listweight[1]))
		self.menuList = list(m_list)

	def exit(self, ret=None):
		if self.sort_mode:
			self.toggleSortMode()
		else:
			self.close()
