# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''MessageBus - Heart of the backend messaging system'''

import threading

from entertainerlib.backend.core.message import Message
from entertainerlib.backend.core.message_handler import MessageHandler
from entertainerlib.backend.core.message_type_priority import MessageType
from entertainerlib.logger import Logger

class MessageBus:
    """
    MessageBus is the heart of the backend messaging system.

    Almost all communication between components goes through this MessageBus.
    Components communicate with Messages, which are delivered to
    MessageHandlers

    via MessageBus. MessageBus knows which MessageHandlers are interested in
    which type of Messages. MessageBus is also aware of MessageHandler
    priorities and this way can serve high priority components first.

    When MessageHandler is registered to the MessageBus there is also another
    parameter besides handler itself. Second parameter is a dictionary that
    defines MessageTypes that registered handler wants to be notified of and
    also priorities for those message types."""

    # This determines number of message types avaialble. In other words, this
    # variable tells how many variables is defined in MessageType class.
    NUMBER_OF_MESSAGE_TYPES = len(
        [k for k, v in vars(MessageType).items() if type(v) is int]
        )

    def __init__(self):
        """
        Create a new MessageBus object.
        """
        # MessageHandlers - index is MessageType and data is a list of
        # tuples (priority, MessageHandler object) that is sorted by
        # priorities.
        #XXX: rockstar - WTF?!  Why is there a list comprehension being used
        # and still only returning an empty list?
        # pylint: disable-msg=W0612
        self.message_handlers = [
            [] for i in range(self.NUMBER_OF_MESSAGE_TYPES)
            ]
        self.lock = threading.Lock()
        self.logger = Logger().getLogger('backend.core.MessageBus')

    def registerMessageHandler(self, message_handler, message_priority_list):
        """
        Register a new MessageHandler to this MessageBus
        @param message_handler: MessageHandler object
        @param message_priority_list: Priority list for this MessageHandler
        """
        if isinstance(message_handler, MessageHandler):
            for key in message_priority_list:
                rule = (message_priority_list[key], message_handler)
                self.message_handlers[key].append(rule)
                self.message_handlers[key].sort() # Keep priority order
        else:
            self.logger.critical(
                "MessageHandler registration failed. Object " +
                repr(message_handler) +" is invalid type.")
            raise TypeError("Only MessageHandlers can be registered!")
        self.logger.debug("MessageHandler '" + str(message_handler) +
                          "' registered to the message bus.")

    def unregisterMessageHandler(self, message_handler):
        """
        Unregister MessageHandler form this MessageBus.
        @param message_handler: MessageHandler object that should be removed
        from bus
        """
        if isinstance(message_handler, MessageHandler):
            for i in range(self.NUMBER_OF_MESSAGE_TYPES):
                if len(self.message_handlers[i]) != 0:
                    rules = self.message_handlers[i]
                    for element in rules:
                        if element[1] is message_handler:
                            del element
        else:
            raise TypeError("Only MessageHandlers can be unregistered!")
        self.logger.debug("MessageHandler '" + str(message_handler) +
                          "' unregistered from the message bus.")

    def notifyMessage(self, message):
        """
        Emit a new Message to this MessageBus.
        @param message: Message object
        """
        if isinstance(message, Message):
            self.lock.acquire() # Lock messagebus
            self.logger.debug("Message bus locked. Message of type '" +
                              str(message.get_type()) + "' is on the bus.")
            handler_list = self.message_handlers[message.get_type()]
            for element in handler_list:
                element[1].handleMessage(message)
            self.lock.release() # Release messagebus lock
        else:
            message = "TypeError occured when message was notified to the bus."
            self.logger.error(message)
            exmessage = "Notified message must be instances of 'Message' type"
            raise TypeError(exmessage)

