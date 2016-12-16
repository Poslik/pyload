# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from pyload.Api import Api, require_perm, Permission, StatusInfo, Interaction
from pyload.utils.fs import join, free_space, exists
from pyload.utils import compare_time

from .apicomponent import ApiComponent


class CoreApi(ApiComponent):
    """ This module provides methods for general interaction with the core, like status or progress retrieval  """

    @require_perm(Permission.All)
    def get_server_version(self):
        """pyLoad Core version """
        return self.pyload.version

    def is_ws_secure(self):
        # needs to use TLS when either requested or webui is also using encryption
        if not self.pyload.config['ssl']['activated'] or self.pyload.config['webui']['https']:
            return False

        if not exists(self.pyload.config['ssl']['cert']) or not exists(self.pyload.config['ssl']['key']):
            self.pyload.log.warning(_('SSL key or certificate not found'))
            return False

        return True

    @require_perm(Permission.All)
    def get_ws_address(self):
        """Gets and address for the websocket based on configuration"""
        if self.is_ws_secure():
            ws = "wss"
        else:
            ws = "ws"

        return "%s://%%s:%d" % (ws, self.pyload.config['webui']['wsPort'])

    @require_perm(Permission.All)
    def get_status_info(self):
        """Some general information about the current status of pyLoad.

        :return: `StatusInfo`
        """
        queue = self.pyload.files.getQueueStats(self.primary_uid)
        total = self.pyload.files.getDownloadStats(self.primary_uid)

        serverStatus = StatusInfo(0,
                                    total[0], queue[0],
                                    total[1], queue[1],
                                    self.isInteractionWaiting(Interaction.All),
                                    not self.pyload.dlm.paused and self.isTimeDownload(),
                                    self.pyload.dlm.paused,
                                    self.pyload.config['reconnect']['activated'] and self.isTimeReconnect(),
                                    self.getQuota())

        for pyfile in self.pyload.dlm.activeDownloads(self.primary_uid):
            serverStatus.speed += pyfile.getSpeed() #bytes/s

        return serverStatus

    @require_perm(Permission.All)
    def get_progress_info(self):
        """ Status of all currently running tasks

        :rtype: list of :class:`ProgressInfo`
        """
        return self.pyload.dlm.getProgressList(self.primary_uid) +\
            self.pyload.threadManager.getProgressList(self.primary_uid)

    def pause_server(self):
        """Pause server: It won't start any new downloads, but nothing gets aborted."""
        self.pyload.dlm.paused = True

    def unpause_server(self):
        """Unpause server: New Downloads will be started."""
        self.pyload.dlm.paused = False

    def toggle_pause(self):
        """Toggle pause state.

        :return: new pause state
        """
        self.pyload.dlm.paused ^= True
        return self.pyload.dlm.paused

    def toggle_reconnect(self):
        """Toggle reconnect activation.

        :return: new reconnect state
        """
        self.pyload.config["reconnect"]["activated"] ^= True
        return self.pyload.config["reconnect"]["activated"]

    def free_space(self):
        """Available free space at download directory in bytes"""
        return free_space(self.pyload.config["general"]["download_folder"])


    def quit(self):
        """Clean way to quit pyLoad"""
        self.pyload.do_kill = True

    def restart(self):
        """Restart pyload core"""
        self.pyload.do_restart = True

    def get_log(self, offset=0):
        """Returns most recent log entries.

        :param offset: line offset
        :return: List of log entries
        """
        filename = join(self.pyload.config['log']['log_folder'], 'log.txt')
        try:
            fh = open(filename, "r")
            lines = fh.readlines()
            fh.close()
            if offset >= len(lines):
                return []
            return lines[offset:]
        except Exception:
            return ['No log available']

    @require_perm(Permission.All)
    def is_time_download(self):
        """Checks if pyload will start new downloads according to time in config.

        :return: bool
        """
        start = self.pyload.config['downloadTime']['start'].split(":")
        end = self.pyload.config['downloadTime']['end'].split(":")
        return compare_time(start, end)

    @require_perm(Permission.All)
    def is_time_reconnect(self):
        """Checks if pyload will try to make a reconnect

        :return: bool
        """
        start = self.pyload.config['reconnect']['startTime'].split(":")
        end = self.pyload.config['reconnect']['endTime'].split(":")
        return compare_time(start, end) and self.pyload.config["reconnect"]["activated"]


if Api.extend(CoreApi):
    del CoreApi