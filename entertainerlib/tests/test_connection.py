# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"Tests ConnectionServer"

import socket

from entertainerlib.backend.core.connection_server import ConnectionServer
from entertainerlib.backend.core.message_bus import MessageBus
from entertainerlib.tests import EntertainerTest

class ConnectionServerTest(EntertainerTest):
    '''Test for entertainerlib.backend.core.connection_server'''

    def setUp(self):
        '''see unittest.TestCase'''
        EntertainerTest.setUp(self)

        self.message_bus = MessageBus()
        port = 45054 # Default port
        self.connection = ConnectionServer(port, self.message_bus)

    def tearDown(self):
        '''see unittest.TestCase'''
        EntertainerTest.tearDown(self)

    def testPortBinding(self):
        '''Test that binding to a used port fails gracefully'''
        port = 45055 # This test assumes that this port is open
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', port))

        #ConnectionServer uses a sys exit command, check for exception
        self.assertRaises(SystemExit, ConnectionServer, port, self.message_bus)

