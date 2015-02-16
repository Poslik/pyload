# -*- coding: utf-8 -*-

from pyload.plugin.internal.DeadHoster import DeadHoster, create_getInfo


class FiredriveCom(DeadHoster):
    __name__    = "FiredriveCom"
    __type__    = "hoster"
    __version__ = "0.05"

    __pattern__ = r'https?://(?:www\.)?(firedrive|putlocker)\.com/(mobile/)?(file|embed)/(?P<ID>\w+)'

    __description__ = """Firedrive.com hoster plugin"""
    __license__     = "GPLv3"
    __authors__     = [("Walter Purcaro", "vuolter@gmail.com")]


getInfo = create_getInfo(FiredriveCom)