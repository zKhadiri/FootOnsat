from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Plugins.Extensions.FootOnSat.ui.interface import FootOnSatNotifDialog
from Plugins.Extensions.FootOnSat.ui.launcher import FootOnsatLauncher
from enigma import addFont, getDesktop

addFont("/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/assets/fonts/miso-bold.ttf", "FootFont", 100, 1)
addFont("/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/assets/fonts/font_default.otf", "ArabicFont", 100, 1)
addFont("/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/assets/fonts/google-icons.ttf", "FootIcons", 100, 1)


def isHD():
	if getDesktop(0).size().width() < 1920:
		return True
	else:
		return False

def main(session, **kwargs):
    if isHD():
        session.open(MessageBox, _('Skin is not supported\nFootOnSat Plugin works only with FHD skins'), MessageBox.TYPE_ERROR)
    else:
        session.open(FootOnsatLauncher)

def sessionstart(reason, **kwargs):
    if reason == 0 and isHD():
        FootOnSatNotifDialog.startNotif(kwargs["session"])

def Plugins(**kwargs):
    Descriptors = []
    Descriptors.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart))
    Descriptors.append(PluginDescriptor(name='FootOnSat', description='Football Fixtures', where=PluginDescriptor.WHERE_PLUGINMENU, icon='logo.png', fnc=main))
    return Descriptors
