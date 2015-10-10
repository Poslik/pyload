# -*- coding: utf-8 -*-

from module.plugins.internal.DeadHoster import DeadHoster, create_getInfo


class WuploadCom(DeadHoster):
    __name      = "WuploadCom"
    __type__    = "hoster"
    __version__ = "0.24"
    __status__  = "testing"

    __pattern__ = r'http://(?:www\.)?wupload\..+?/file/((\w+/)?\d+)(/.*)?'
    __config__  = []  #@TODO: Remove in 0.4.10

    __description__ = """Wupload.com hoster plugin"""
    __license__     = "GPLv3"
    __authors__     = [("jeix", "jeix@hasnomail.de"),
                       ("Paul King", None)]


getInfo = create_getInfo(WuploadCom)
