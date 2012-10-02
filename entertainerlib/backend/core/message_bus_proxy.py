# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Used to connect client processes to backend MessageBus'''

import socket
import cPickle
import threading
from cStringIO import StringIO

from entertainerlib.configuration import Configuration

class MessageBusProxy(threading.Thread):
    """
    MessageBusProxy connects client processes to the backend's MessageBus.

    MessageBusProxy hides IPC (inter process communication) from clients and
    it provides easy way to send and receive Messages to/from backends
    MessageBus.

    Under the hood MessageBusProxy transfers Message objects via socket
    connection. Connection is made to backend's ConnectionServer object which
    spawns a new thread for each client connection.

    If your client doesn't want to receive any messages - only send them,
    them do NOT give MessageHandler as a constructor parameter and do NOT
    give message_type_dictionary as a paramter and do NOT call
    proxy_object.start(). If you're client is interested in messages,
    set MessageHandler, dictionary and call start() right after
    connectToMessageBus() call.
    """

    def __init__(self, message_type_dictionary=None, message_handler=None,
        client_name="Unknown client"):
        """
        Create a new MessageBusProxy object
        @param message_type_dictionary: Dictionary that contains message types
        @param message_handler: MessageHandler object
        @param client_name: Name of the client (as string)
        """
        threading.Thread.__init__(self)
        if message_type_dictionary is None:
            self.message_type_dictionary = {}
        else:
            self.message_type_dictionary = message_type_dictionary
        self.message_handler = message_handler
        self.client_name = client_name
        self.socket_to_server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
            )
        self.socket_as_file = self.socket_to_server.makefile()
        self.config = Configuration()

    def connectToMessageBus(self):
        """
        Connects to backend's MessageBus.

        After this call, all interesting messages are delivered to local
        MessageHandler.
        """
        # Open socket
        self.socket_to_server.connect(('localhost', self.config.port))

        # Send client name
        self.socket_to_server.sendall(self.client_name + "\n")

        # Send message type/priority dictionary
        message_types = cPickle.dumps(self.message_type_dictionary,
                                      cPickle.HIGHEST_PROTOCOL)
        self.socket_to_server.sendall(message_types + "\n")

    def disconnectFromMessageBus(self):
        """Disconnect from backend's MessageBus"""
        self.socket_to_server.shutdown(socket.SHUT_RDWR)
        self.socket_to_server.close()

    def sendMessage(self, message):
        """Send messaged to backend's MessageBus"""
        message_str = cPickle.dumps(message, cPickle.HIGHEST_PROTOCOL)
        self.socket_to_server.sendall(message_str)
        self.socket_to_server.sendall("\nEND_OF_MESSAGE_OBJECT\n")

    def run(self):
        '''See threading.Thread'''
        obj_buffer = StringIO()
        while True:
            line = self.socket_as_file.readline()
            if line == "END_OF_MESSAGE_OBJECT\n":
                message = cPickle.loads(obj_buffer.getvalue())
                if self.message_handler is not None:
                    self.message_handler.handleMessage(message)
                else:
                    raise Exception("Proxy doesn't have MessageHandler object!")
                obj_buffer = StringIO() # Reset buffer
            else:
                obj_buffer.write(line)

