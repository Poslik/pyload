# -*- coding: utf-8 -*-

import random
import re

import pycurl

from module.common.json_layer import json_loads, json_dumps
from module.network.HTTPRequest import BadHeader
from module.network.RequestFactory import getRequest as get_request
from module.plugins.internal.Addon import Addon


class TransmissionRPC(Addon):
    __name      = "TransmissionRPC"
    __type__    = "hook"
    __version__ = "0.12"
    __status__  = "testing"

    __pattern__ = r"https?://.+\.torrent|magnet:\?.+"
    __config__  = [("activated", "bool", "Activated"           , False                                   ),
                   ("rpc_url"  , "str" , "Transmission RPC URL", "http://127.0.0.1:9091/transmission/rpc")]

    __description__ = """Send torrent and magnet URLs to Transmission Bittorent daemon via RPC"""
    __license__     = "GPLv3"
    __authors__     = [("GammaC0de", None)]


    def init(self):
        self.event_map = {'linksAdded': "links_added"}


    def links_added(self, links, pid):
        pattern = re.compile(self.__pattern)
        urls = [link for link in links if pattern.match(link)]

        for url in urls:
            self.log_debug("Sending link: %s" % url)
            self.send_to_transmission(url)
            links.remove(url)


    def send_to_transmission(self, url):
        transmission_rpc_url = self.get_config('rpc_url')
        client_request_id = self.__name__ + "".join(random.choice('0123456789ABCDEF') for _i in xrange(4))
        req = get_request()

        try:
            response = self.load(transmission_rpc_url,
                                 post=json_dumps({'arguments': {'filename': url},
                                                  'method'   : 'torrent-add',
                                                  'tag'      : client_request_id}),
                                 req=req)

        except BadHeader, e:
            if e.code == 409:
                headers = dict(re.findall(r"(?P<name>.+?): (?P<value>.+?)\r?\n", req.header))
                session_id = headers['X-Transmission-Session-Id']
                req.c.setopt(pycurl.HTTPHEADER, ["X-Transmission-Session-Id: %s" % session_id])
                try:
                    response = self.load(transmission_rpc_url,
                                         post=json_dumps({'arguments': {'filename': url},
                                                          'method'   : 'torrent-add',
                                                          'tag'      : client_request_id}),
                                         req=req)

                except Exception, e:
                     self.log_error(e, trace=True)
                     return

            else:
                 self.log_error(e, trace=True)
                 return

        except Exception, e:
             self.log_error(e, trace=True)
             return

        try:
            res = json_loads(response)
            if "result" in res:
                self.log_debug("Result: %s" % res['result'])

        except Exception, e:
            self.log_error(e, trace=True)
