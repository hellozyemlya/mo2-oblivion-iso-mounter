import mobase

from .mounter import OblivionIsoMounter


def createPlugin() -> mobase.IPlugin:
    return OblivionIsoMounter()
