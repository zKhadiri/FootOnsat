from Plugins.Plugin import PluginDescriptor
from Plugins.Extensions.FootOnSat.ui.interface import FootOnSatNotifDialog
from Plugins.Extensions.FootOnSat.ui.launcher import FootOnsatLauncher
from enigma import addFont

addFont("/usr/lib/enigma2/python/Plugins/Extensions/FootOnSat/assets/fonts/miso-bold.ttf", "Myfont", 100, 1)

def main(session, **kwargs):
    session.open(FootOnsatLauncher)

def sessionstart(reason, **kwargs):
    if reason == 0:
        FootOnSatNotifDialog.startNotif(kwargs["session"])

def Plugins(**kwargs):
    Descriptors=[]
    Descriptors.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart))
    Descriptors.append(PluginDescriptor(name='FootOnSat', description='Football Fixtures', where=PluginDescriptor.WHERE_PLUGINMENU, icon='logo.png', fnc=main))
    return Descriptors