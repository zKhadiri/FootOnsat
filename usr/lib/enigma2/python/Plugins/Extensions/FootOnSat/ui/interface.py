# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Button import Button
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Components.NimManager import nimmanager, getConfigSatlist
from enigma import eTimer, gRGB, loadPNG, gPixmapPtr, RT_WRAP, ePoint, BT_SCALE, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, eConsoleAppContainer
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Components.NimManager import nimmanager, getConfigSatlist
import json
import random
import math
from time import strftime
from datetime import datetime, timedelta
from twisted.web.client import getPage, downloadPage
from twisted.internet.ssl import ClientContextFactory
from twisted.internet._sslverify import ClientTLSOptions
from sqlite3 import connect
from sys import version_info
try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse

PY3 = version_info[0] == 3


DB_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/db/footonsat.db'


def readFromFile(filename):
	_file = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/{}".format(filename))
	with open(_file, 'r') as f:
		return f.read()


class WebClientContextFactory(ClientContextFactory):
	def __init__(self, url=None):
		domain = urlparse(url).netloc
		self.hostname = domain
	
	def getContext(self, hostname=None, port=None):
		ctx = ClientContextFactory.getContext(self)
		if self.hostname and ClientTLSOptions is not None: # workaround for TLS SNI
			ClientTLSOptions(self.hostname, ctx)
		return ctx

class FootOnSat(Screen):

	def __init__(self, session, link, *args):
		self.session = session
		Screen.__init__(self, session)
		skin = "assets/skin/FHD/interface.xml"
		self.skin = readFromFile(skin)
		self["setupActions"] = ActionMap(["FootOnsatActions"],
		{
			"ok": self.ok,
			"down": self.listDOWN,
			"up": self.listUP,
			"left": self.left,
			"right": self.right,
			"blue": self.keyBlue,
			"cancel": self.exit,
		}, -1)
		self.link = link
		self["counter"] = Label()
		self["channel"] = Label()
		self["sat"] = Label()
		self["freq"] = Label()
		self["enc"] = Label()
		self["key_blue"] = Button(_("Scan"))
		self["key_blue"].hide()
		self["list1"] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self["list2"] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.selectedList = self["list1"]
		self.canScan = False
		self.channelData = []
		self.matches = []
		self.create_table()
		self.callAPI()

	def onWindowShow(self):
		self["list1"].onSelectionChanged.append(self.getChannels)
		self.enablelist1()
		self.disablelist2()
		self.iniMenu()

	def iniMenu(self):
		if len(self.matches) > 0:
			res = []
			gList = []
			self["list1"].l.setItemHeight(175)
			self["list1"].l.setFont(0, gFont('Regular', 28))
			for i in range(0, len(self.matches)):
				match = self.matches[i][0]
				match_date = self.matches[i][1]
				compet = self.matches[i][2]
				team1 = self.matches[i][3]
				team2 = self.matches[i][4]
				flagTeam1 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/{}.png".format(team1))
				flagTeam2 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/{}.png".format(team2))
				banner = FootOnSat.setCompet(compet.lower())
				match_date = self.getTime(match_date)
				if not fileExists(flagTeam1):
					flagTeam1 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/default.png")
				if not fileExists(flagTeam2):
					flagTeam2 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/default.png")
				if self.checkIfexist(match):
					notif = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/icon/notif_on.png")
				else:
					notif = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/icon/notif_off.png")
				res.append(MultiContentEntryText())
				res.append(MultiContentEntryPixmapAlphaBlend(pos=(420, 69), size=(40, 30), png=loadPNG(flagTeam1)))
				res.append(MultiContentEntryPixmapAlphaBlend(pos=(1092, 69), size=(40, 30), png=loadPNG(flagTeam2)))
				res.append(MultiContentEntryPixmapAlphaTest(pos=(65, 6), size=(320, 163), png=loadPNG(banner), flags=BT_SCALE))
				res.append(MultiContentEntryPixmapAlphaBlend(pos=(-20, 63), size=(70, 50), png=loadPNG(notif)))
				res.append(MultiContentEntryText(pos=(467, 66), size=(570, 36), font=0, flags=RT_VALIGN_CENTER | RT_HALIGN_LEFT, text=str(match)))
				res.append(MultiContentEntryText(pos=(420, 120), size=(450, 36), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text="Kick-off : " + str(match_date)))
				res.append(MultiContentEntryText(pos=(420, 15), size=(785, 36), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=str(compet)))
				gList.append(res)
				res = []
			self["list1"].setList(gList)
			self.updateCounter()
		else:
			self.session.openWithCallback(self.exit, MessageBox, _('No schedules in this section at this time'), MessageBox.TYPE_INFO, timeout=10)

	def enablelist1(self):
		instance = self["list1"].instance
		instance.setSelectionEnable(1)

	def enablelist2(self):
		instance = self["list2"].instance
		instance.setSelectionEnable(1)

	def disablelist1(self):
		instance = self["list1"].instance
		instance.setSelectionEnable(0)

	def disablelist2(self):
		instance = self["list2"].instance
		instance.setSelectionEnable(0)

	def left(self):
		if self.selectedList == self["list2"]:
			self.selectedList = self["list1"]
			self.enablelist1()
			self.disablelist2()
			self.resetChannelinfo()
		elif self.selectedList == self["list1"]:
			self.exit()

	def right(self):
		if self.selectedList.getCurrent():
			self.selectedList = self["list2"]
			self.enablelist2()
			self.updateChannelData()

	def listDOWN(self):
		if self.selectedList.getCurrent():
			instance = self.selectedList.instance
			instance.moveSelection(instance.moveDown)
		if self.selectedList == self["list1"]:
			self.disablelist2()
			self.updateCounter()
			self.resetChannelinfo()
		if self.selectedList == self["list2"]:
			self.updateChannelData()

	def listUP(self):
		if self.selectedList.getCurrent():
			instance = self.selectedList.instance
			instance.moveSelection(instance.moveUp)
		if self.selectedList == self["list1"]:
			self.disablelist2()
			self.updateCounter()
			self.resetChannelinfo()
		if self.selectedList == self["list2"]:
			self.updateChannelData()

	def create_table(self):
		with connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute('CREATE TABLE IF NOT EXISTS LIVE_NOTIF (MATCH TEXT primary key , COMPET TEXT , DATE TEXT , TEAM1_FLAG TEXT , TEAM2_FLAG TEXT , FIRST_NOTIF TEXT , FIRST_NOTIF_STATUS TEXT , LIVE_NOTIF_STATUS TEXT,MESSAGE TEXT)')

	def ok(self):
		if self.selectedList == self["list1"] and len(self.matches) > 0:
			index = self['list1'].getSelectionIndex()
			if PY3:
				match = self.matches[index][0]
				match_date = self.getTime(self.matches[index][1])
				compet = self.matches[index][2]
				flag1 = self.matches[index][3]
				flag2 = self.matches[index][4]
			else:
				match = self.matches[index][0].decode('utf8')
				match_date = self.getTime(self.matches[index][1].decode('utf8'))
				compet = self.matches[index][2].decode('utf8')
				flag1 = self.matches[index][3].decode('utf8')
				flag2 = self.matches[index][4].decode('utf8')

			if datetime.strptime(match_date, "%H:%M - %Y-%m-%d") > datetime.now():
				if self.checkIfexist(match):
					with connect(DB_PATH) as conn:
						cur = conn.cursor()
						cur.execute("DELETE FROM LIVE_NOTIF WHERE MATCH = ?", (match,))
				else:
					if not self.sameDate(match_date):
						with connect(DB_PATH) as conn:
							cur = conn.cursor()
							first_notif, message = self.setFirstNotifTime(match_date)
							cur.execute("INSERT INTO LIVE_NOTIF(MATCH,COMPET,DATE,TEAM1_FLAG,TEAM2_FLAG,FIRST_NOTIF,FIRST_NOTIF_STATUS,LIVE_NOTIF_STATUS,MESSAGE) values (?,?,?,?,?,?,?,?,?)", (
								match, compet, match_date, flag1, flag2, first_notif, "Waiting", "Waiting", message,))
				self.iniMenu()

	def setFirstNotifTime(self, dt):
		dt_obj = datetime.strptime(dt, "%H:%M - %Y-%m-%d")
		now = datetime.now()
		duration = dt_obj - now
		duration_in_s = duration.total_seconds()
		minutes = divmod(duration_in_s, 60)[0]
		if minutes < 30:
			first_notif = (dt_obj - timedelta(minutes=minutes / 2)).strftime("%H:%M - %Y-%m-%d")
			message = "Kick-off in {} minutes".format(int(minutes / 2))
		else:
			first_notif = (dt_obj - timedelta(minutes=30)).strftime("%H:%M - %Y-%m-%d")
			message = "Kick-off in 30 minutes"
		return [first_notif, message]

	def sameDate(self, dt):
		with connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute("SELECT DATE FROM LIVE_NOTIF WHERE DATE = ?", (dt,))
			data = cur.fetchone()
			if data is None:
				return False
			else:
				return True

	def checkIfexist(self, match):
		if PY3:
			match = match
		else:
			match = match.decode('utf-8')
		with connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute("SELECT MATCH FROM LIVE_NOTIF WHERE MATCH = ?", (match,))
			data = cur.fetchone()
			if data is None:
				return False
			else:
				return True

	def getTime(self, match_date):
		timezone = strftime("%z")
		if timezone.startswith('+') and timezone != '+0000':
			dif = int(timezone.replace('+', '').replace('00', ''))
			calc = (datetime.strptime(match_date, '%H:%M - %Y-%m-%d') + timedelta(hours=dif)).strftime('%H:%M - %Y-%m-%d')
		elif timezone == '+0000':
			calc = match_date
		else:
			dif = int(timezone.replace('-', '').replace('00', ''))
			calc = (datetime.strptime(match_date, '%H:%M - %Y-%m-%d') - timedelta(hours=dif)).strftime('%H:%M - %Y-%m-%d')
		return calc

	def updateCounter(self):
		if len(self.matches) > 0:
			index = self['list1'].getSelectionIndex()
			total_pages = int(math.ceil(float(len(self.matches)) / 4))
			current_page = int(math.ceil((index) // 4)) +1
			self["counter"].setText("{}/{}".format(current_page, total_pages))

	@classmethod
	def setCompet(cls, compet):
		with open('/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/assets/compet/package.json', 'r') as f:
			data = json.load(f)
		for c in data['compet']:
			if c['label'] in compet:
				return resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/compet/FHD/{}.png".format(c['banner']))
		banner = random.choice(['default', 'default1', 'default2', 'default3'])
		return resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/compet/default/FHD/{}.png".format(banner))

	def callAPI(self):
		url = 'https://raw.githubusercontent.com/zKhadiri/footonsat-api/main/{}.json'.format(self.link)
		sniFactory = WebClientContextFactory(url)
		getPage(str.encode(url), contextFactory=sniFactory).addCallback(self.getData).addErrback(self.error)

	def error(self, error=None):
		if error:
			self.session.openWithCallback(self.exit, MessageBox, _('An Unexpected HTTP Error Occurred During The API Request !!'), MessageBox.TYPE_ERROR, timeout=10)

	def getData(self, data):
		list = []
		self.js = json.loads(data)
		if self.js['footonsat'] != []:
			for match in self.js['footonsat']:
				try:
					match_date = datetime.strptime(match['date'] + ' ' + match['time'], '%Y-%m-%d %H:%M')
					last_3 = datetime.strptime((datetime.now() - timedelta(minutes=130)).strftime('%Y-%m-%d %H:%M'), "%Y-%m-%d %H:%M")
					if match_date > last_3:
						list.append((str(match['match']), str(match['time']) + ' - ' + str(match['date']), str(match['compet']),
									str(match['flags']['team1']), str(match['flags']['team2']), ))
				except KeyError:
					pass
			self.matches = list
			self.onWindowShow()
		else:
			self.session.openWithCallback(self.exit, MessageBox, _('No schedules in this section at this time'), MessageBox.TYPE_ERROR, timeout=10)

	def getChannels(self):
		list = []
		res = []
		gList = []
		self["list2"].l.setItemHeight(50)
		self["list2"].l.setFont(0, gFont('Regular', 30))
		index = self['list1'].getSelectionIndex()
		if len(self.matches) > 0:
			self.match = self.matches[index][0]
			for data in self.js['footonsat']:
				try:
					if data['related_to'] == self.match:
						list.append((str(data['channel']), str(data['sat']), str(data['freq']), str(data['encry']), str(data['link'])))
						res.append(MultiContentEntryText())
						res.append(MultiContentEntryText(pos=(7, 6), size=(510, 40), font=0, flags=RT_VALIGN_CENTER | RT_HALIGN_LEFT, text=str(data['channel'])))
						gList.append(res)
						res = []
				except KeyError:
					pass
			self["list2"].setList([])
			self["list2"].setList(gList)
			self.channelData = list

	def updateChannelData(self):
		if len(self.channelData) > 0:
			index = self['list2'].getSelectionIndex()
			self["channel"].setText(self.channelData[index][0])
			self["sat"].setText(self.channelData[index][1])
			self["freq"].setText(self.channelData[index][2])
			self["enc"].setText(self.channelData[index][3])
			if 'V' in self.channelData[index][2] or 'H' in self.channelData[index][2]:
				self['key_blue'].show()
				self.canScan = True
			else:
				self['key_blue'].hide()
				self.canScan = False

	def resetChannelinfo(self):
		self["channel"].setText("")
		self["sat"].setText("")
		self["freq"].setText("")
		self["enc"].setText("")
		self['key_blue'].hide()
		self.canScan = False

	def keyBlue(self):
		if self.canScan:
			self.scan()

	def scan(self):
		if (nimmanager.hasNimType("DVB-S")):
			nims = nimmanager.getNimListOfType('DVB-S')
			nimList = []
			self.openatv = False
			self.openpli = False
			for elem in nims:
				nim = nimmanager.getNimConfig(elem)
				if hasattr(nim, 'dvbs'):
					self.openatv = True
					if nim.dvbs.configMode.value not in ('loopthrough', 'satposdepends',
														'nothing'):
						nimList.append(elem)
				elif hasattr(nim, 'configMode'):
					self.openpli = True
					if nim.configMode.value not in ('loopthrough', 'satposdepends', 'nothing'):
						nimList.append(elem)

			index = self['list2'].getSelectionIndex()
			freq = self.channelData[index][2].split(' ')[0]
			symbolrate = self.channelData[index][2].split(' ')[2]
			pos = self.channelData[index][1].split(' ')[-1].replace('°', ' ').split(' ')
			sat = self.getSat(pos)
			fec = self.channelData[index][2].split(' ')[-1]
			polarization = 'V' if 'V' in self.channelData[index][2] else 'H'

			if len(nimList) == 0:
				self.session.open(MessageBox, _('Satellite frontend Not found!'), MessageBox.TYPE_ERROR, timeout=10)
			elif fileExists('/var/lib/dpkg/status'):
				from Plugins.Extensions.FootOnSat.satfinder.dreamos import Satfinder
				self.session.open(Satfinder, self.getfeid(), freq, symbolrate, sat, polarization, fec)
			elif self.openatv:
				from Plugins.Extensions.FootOnSat.satfinder.openatv import Satfinder
				self.session.open(Satfinder, freq, symbolrate, sat, polarization, fec)
			elif self.openpli:
				from Plugins.Extensions.FootOnSat.satfinder.openpli import Satfinder
				self.session.open(Satfinder, freq, symbolrate, sat, polarization, fec)
			else:
				self.session.open(MessageBox, 'Satfinder Is not compatible with this image', MessageBox.TYPE_ERROR, timeout=10)
		else:
			self['key_blue'].hide()

	def getfeid(self):
		nims = nimmanager.getNimListOfType("DVB-S")
		nimList = []
		for x in nims:
			nim = nimmanager.getNimConfig(x)
			if not nim.sat.configMode.value in ("loopthrough", "satposdepends", "nothing"):
				nimList.append(x)
		if len(nimList) == 1:
			return nimList[0]

	def getSat(self, pos):
		if pos[-1] == 'w':
			sat = int(float(pos[0]) * -1 * 10 + 3600)
		else:
			sat = int(float(pos[0]) * 10)
		return sat

	def exit(self, ret=None):
		self.close()


class FootOnSatNotif():
	def __init__(self):
		self.dialog = None

	def startNotif(self, session):
		self.dialog = session.instantiateDialog(FootOnsatNotifScreen)


FootOnSatNotifDialog = FootOnSatNotif()


class FootOnsatNotifScreen(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		skin = "assets/skin/FHD/FootOnsatNotif.xml"
		self.skin = readFromFile(skin)
		self['match'] = Label()
		self['message'] = Label()
		self['compet'] = Pixmap()
		self['flag1'] = Pixmap()
		self['flag2'] = Pixmap()
		self['live'] = Pixmap()
		self.container = eConsoleAppContainer()
		self.FootOnsatTimer = eTimer()
		try:
			self.FootOnsatTimer.timeout.get().append(self.checkforNotif)
		except:
			self.FootOnsatTimer_conn = self.FootOnsatTimer.timeout.connect(self.checkforNotif)
		self.FootOnsatTimer.start(15000)
		self.onhideTimer = eTimer()
		try:
			self.onhideTimer.timeout.get().append(self.hideNotif)
		except:
			self.onhideTimer_conn = self.onhideTimer.timeout.connect(self.hideNotif)

	def checkforNotif(self):
		if fileExists(DB_PATH):
			self.deloldRecords()
			with connect(DB_PATH) as conn:
				cur = conn.cursor()
				rows = cur.execute("select * from LIVE_NOTIF")
				rows = rows.fetchall()
				now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M'), "%Y-%m-%d %H:%M")
				if len(rows) > 0:
					for row in rows:
						first_notif = datetime.strptime(row[5], "%H:%M - %Y-%m-%d")
						live_notif = datetime.strptime(row[2], "%H:%M - %Y-%m-%d")
						if first_notif == now and row[6] == 'Waiting':
							cur.execute("UPDATE LIVE_NOTIF set FIRST_NOTIF_STATUS = ?  WHERE FIRST_NOTIF = ? and MATCH = ?", ("Done", row[5], row[0],))
							self.notify(row[0].strip(), row[1], row[3], row[4], row[8])
						if live_notif == now and row[7] == 'Waiting':
							cur.execute("DELETE FROM LIVE_NOTIF WHERE DATE = ? and MATCH = ?", (row[2], row[0],))
							self.notify(row[0].strip(), row[1], row[3], row[4])

	def deloldRecords(self):
		with connect(DB_PATH) as conn:
			cur = conn.cursor()
			rows = cur.execute("select DATE from LIVE_NOTIF")
			rows = rows.fetchall()
			today = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M'), "%Y-%m-%d %H:%M")
			if len(rows) > 0:
				for row in rows:
					record_date = datetime.strptime(row[0], "%H:%M - %Y-%m-%d")
					if today > record_date:
						cur.execute("DELETE FROM LIVE_NOTIF WHERE DATE = ?", (row[0],))

	def notify(self, match, compet, team1, team2, message=None):
		if self.instance:
			if FootOnSatNotifDialog.dialog is not None:
				self['match'].setText(_(str(match)))
				if message:
					self['live'].hide()
					self['message'].setText(str(message))
				else:
					self['live'].show()
					self['message'].setText("")
				banner = FootOnSat.setCompet(compet.lower())
				self['compet'].instance.setPixmapFromFile(banner)
				flag1 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/{}.png".format(team1))
				flag2 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/{}.png".format(team2))
				if not fileExists(flag1):
					flag1 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/default.png")
				if not fileExists(flag2):
					flag2 = resolveFilename(SCOPE_PLUGINS, "Extensions/FootOnSat/assets/flags/default.png")
				self['flag1'].instance.setPixmapFromFile(flag1)
				self['flag2'].instance.setPixmapFromFile(flag2)
				self.container.execute('aplay /usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/assets/sound/notif1.wav')
				FootOnSatNotifDialog.dialog.show()
				self.onhideTimer.start(8000)

	def hideNotif(self):
		FootOnSatNotifDialog.dialog.hide()
