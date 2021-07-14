import base64
from typing import List

from PyQt5.QtCore import qCritical, QCoreApplication, qInfo
from PyQt5.QtWidgets import QWidget
from mobase import IOrganizer, PluginSetting, VersionInfo, IPlugin
import subprocess


class OblivionIsoMounter(IPlugin):
    def __init__(self):
        super().__init__()
        self._organizer: IOrganizer = None
        self._parent: QWidget = None

    def author(self) -> str:
        return "hellozyemlya"

    def description(self) -> str:
        return "Automatically mounts Oblivion game ISO image for localized legal distributions."

    def init(self, organizer: IOrganizer) -> bool:
        self._organizer = organizer
        if not self._organizer.onAboutToRun(lambda app_name: self._do_mount_iso(app_name)):
            qCritical("Unable to register start callback.")
            return False
        return True

    def name(self) -> str:
        return "Oblivion ISO Mounter"

    def settings(self) -> List[PluginSetting]:
        return [
            PluginSetting("enabled", self.__tr("Enable automatic image mounting"), False),
            PluginSetting("isoPath", self.__tr("ISO image path"), "")
        ]

    def version(self) -> VersionInfo:
        return VersionInfo(0, 0, 0, 1)

    def __tr(self, str_):
        return QCoreApplication.translate("OblivionIsoMounter", str_)

    @property
    def _iso_path(self) -> str:
        return self._organizer.pluginSetting(self.name(), 'isoPath')

    def _is_oblivion(self, app_name: str) -> bool:
        return self._organizer.pluginSetting(self.name(), "enabled") and app_name.lower().endswith(
            "oblivion.exe") and "oblivion" in self._organizer.managedGame().name().lower()

    def _do_mount_iso(self, app_name: str) -> bool:
        if self._is_oblivion(app_name):
            qInfo(f"Mounting Oblivion ISO: {self._iso_path}")
            res = subprocess.run(
                [
                    "powershell.exe",
                    "-WindowStyle", "Hidden",
                    "-NoProfile",
                    "-NonInteractive",
                    "-EncodedCommand", self._iso_mount_command()
                ],
                stderr=subprocess.STDOUT)
            if res.returncode != 0:
                qCritical(res.stdout.decode())
        else:
            return True
        return True

    def _iso_mount_command(self) -> str:
        cmd = f'if(!(Get-DiskImage -ImagePath "{self._iso_path}").Attached){{Mount-DiskImage -ImagePath "{self._iso_path}"}}'
        return base64.encodebytes(cmd.encode("utf-16-le")).decode()
