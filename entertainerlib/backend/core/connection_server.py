# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Socket server that listens for incoming connections'''

import sys
import socket
import threading

from entertainerlib.backend.core.client_connection import ClientConnection

from entertainerlib.logger import Logger

class ConnectionServer(threading.Thread):
    """
    Connection server listens incoming connections.

    On incoming connection ConnectionServer spawns a new ClientConnection
    thread that handles connection. This thread is registered to the
    MessageBus. This way backend can handle multiple connections
    simultaneously.
    """

    def __init__(self, port, message_bus):
        """
        Creates a new ConnectionServer object
        @param port: Port number for this server
        @param message_bus: Bind connecting client to this MessageBus object
        """
        threading.Thread.__init__(self)
        self.message_bus = message_bus # Message bus
        self.logger = Logger().getLogger('backend.core.ConnectionServer')
        # Is ConnectionServer active (listening incoming connections)
        self.active = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind(('localhost', port))
        except socket.error, e:
            message = e[1]
            self.logger.error("Socket failed to bind. %s" % message)
            # socket binding is critical to the backend, so exit
            sys.exit(1)
        self.server_socket.listen(2)

    # Overrides method from Thread class
    def run(self):
        """Execute a new thread of control. Starts listening connections."""
        # XXX: laymansterms - I've short circuited the connection server by
        # setting active to False, preventing it from running. This was to stop
        # a bug that prevented the application from closing.
        self.active = False
        self.logger.debug("ConnectionServer waiting incoming connections")
        while self.active:
            client_socket = self.server_socket.accept()[0]
            self.logger.debug("Incoming connection accepted")
            client_connection = ClientConnection(client_socket,
                                                 self.message_bus)
            client_connection.start()

