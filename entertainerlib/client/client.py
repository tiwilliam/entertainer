# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Entertainer client.'''

import sys

import gtk
from twisted.internet import gtk2reactor
gtk2reactor.install() # Install the gtk2 reactor before import the real reactor
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.python.log import startLogging

from entertainerlib.client.medialibrary.music import MusicLibrary
from entertainerlib.client.medialibrary.images import ImageLibrary
from entertainerlib.client.medialibrary.videos import VideoLibrary
from entertainerlib.configuration import Configuration
from entertainerlib.gui.user_interface import UserInterface
from entertainerlib.gui.system_tray_icon import SystemTrayIcon
from entertainerlib.network.local.client import EntertainerLocalClientProtocol


class Client(object):
    '''This is a client application of Entertainer. Entertainer's client
    hooks into the server, and then provides a user interface for the data the
    server creates.'''

    def __init__(self):
        config = Configuration()
        music_library = MusicLibrary()
        image_library = ImageLibrary()
        video_library = VideoLibrary()
        self.ui = UserInterface(image_library, music_library, video_library,
            self.quit_client)

        if config.tray_icon_enabled:
            SystemTrayIcon(self.quit_client, self.toggle_interface_visibility)

        startLogging(sys.stdout)
        client = EntertainerLocalClientProtocol

        ClientCreator(reactor, client)
#        ClientCreator(reactor, client).connectTCP(
#            config.network_options['host'],
#            config.network_options['port'])

    def start(self):
        '''Start the necessary main loop.'''
        self.ui.start_up()
        self.interface_visible = True
        gtk.gdk.threads_enter()
        reactor.run()
        gtk.gdk.threads_leave()

    def quit_client(self):
        '''Close the client.'''
        reactor.stop()
        sys.exit(0)

    def toggle_interface_visibility(self):
        '''Toggle between showing and hiding the interface's visibility.'''
        if self.interface_visible:
            self.ui.hide()
            self.interface_visible = False
        else:
            self.ui.show()
            self.interface_visible = True

