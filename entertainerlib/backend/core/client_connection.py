# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Connects socket client to backend's message bug'''

import cPickle
from cStringIO import StringIO
import threading

# Messaging system
from entertainerlib.backend.core.message_handler import MessageHandler

from entertainerlib.logger import Logger

class ClientConnection(threading.Thread, MessageHandler):
    """
    Client connection object is an abstraction of connected client.

    This MessageHandler simply forwards all messages to the client process.
    It also reads messages from socket (client process) and forwards them
    to backend's MessageBus. This means that ClientConnection binds backend's
    MessageBus to client processes.
    """

    def __init__(self, socket, message_bus):
        """
        Create a new client connection
        @param socket: Socket object
        @param message_bus: MessageBus object
        """
        threading.Thread.__init__(self)
        MessageHandler.__init__(self)
        self.message_bus = message_bus
        self.logger = Logger().getLogger('backend.core.ClientConnection')
        self.client_out = socket
        self.client = socket.makefile()
        self.client_name = "Unknown" # Client name
        self.message_bus_connected = False # Is connected to the message bus

    def run(self):
        """
        Forward received Message objects to backend's message bus. This method
        spawns a new thread.
        """
        # Receive name
        received_name = self.client.readline()
        # Removes '\n' that indicated message end
        self.client_name = received_name[:-1]
        self.setName("Backend: " + self.client_name) # Thread name

        # Receive dictionary
        dict_str = self.client.readline()
        dictionary = None
        dictionary = cPickle.loads(dict_str[:-1])

        # This client to the message bus if desired
        if dictionary != None and len(dictionary) > 0:
            self.message_bus.registerMessageHandler(self, dictionary)
            self.message_bus_connected = True

        # works as a buffer for incoming message object
        obj_buffer = StringIO()
        while True:
            line = self.client.readline()
            if line == "END_OF_MESSAGE_OBJECT\n":
                message = cPickle.loads(obj_buffer.getvalue())
                self.message_bus.notifyMessage(message)
                obj_buffer = StringIO() # Reset buffer
            elif line == "":
                break # Client closed the socket connection
            else:
                obj_buffer.write(line)

        if self.message_bus_connected:
            self.message_bus.unregisterMessageHandler(self)
        self.client.close() # Connection closed -> This thread dies

    # Implements MessageHandler interface
    def handleMessage(self, message):
        """
        Forward message from the message bus to the client.
        @param message: Received Message object
        """
        message_str = cPickle.dumps(message, cPickle.HIGHEST_PROTOCOL)
        self.client_out.sendall(message_str)
        self.client_out.sendall("\nEND_OF_MESSAGE_OBJECT\n")

