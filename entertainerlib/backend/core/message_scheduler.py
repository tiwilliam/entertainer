# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Manage generating messages to the message bus'''

import random

from entertainerlib.backend.core.message_generator import MessageGenerator

class MessageScheduler(object):
    """
    MessageScheduler generates scheduled messages to the message bus.

    Adding a new message to scheduler doesn't emit message to message bus
    immediately. First scheduler waits random amount of time between 0-5min.
    After that scheduler waits set time interval. After this message is emitted
    to message bus between time intevals. So extra time is waited only once.
    This prevents all messages to be emitted at the same time to the bus.
    """

    def __init__(self, message_bus):
        """
        Create a MessageScheduler object
        @param message_bus: MessageBus where generated messages will be
        notified
        """
        # Message bus where generated messages are notified.
        self.message_bus = message_bus
        # Tuple items are (Message, MessageGenerator (thread), interval)
        self.scheduled_messages = []

    def addMessage(self, message, interval):
        """
        Schedule a new message
        @param message: Message object
        @param interval: Time interval between generating message. (in seconds)
        """
        offset = random.randint(0, 300) # Random offset between 0-5 minutes
        msg_thread = MessageGenerator(message, self.message_bus, interval,
            offset)
        msg_thread.start()
        self.scheduled_messages.append((message, msg_thread, interval))

    def removeMessage(self, message):
        """
        Remove a scheduled message
        @param message: Remove this Message object from scheduling
        """
        for element in self.scheduled_messages:
            if element[0] is message:
                # When sleep ends the thread will die
                element[1].stopGenerator()
                del element

    def changeIntervalForMessage(self, message, new_interval):
        """
        Change the time interval for already scheduled message. Waiting starts
        at the beginning of new interval value.
        @param message: Message object which time interval want to be changed
        @param new_interval: New time interval for this message (in seconds)
        """
        for element in self.scheduled_messages:
            if element[0] is message:
                element[1].stopGenerator()
                t = MessageGenerator(message, self.message_bus, new_interval, 0)
                element[1] = t

