# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Generates messages to the message bus'''

import threading
import time

class MessageGenerator(threading.Thread):
    """
    Thread that generates Messages to the Messagebus.
    """

    def __init__(self, message, message_bus, interval, offset):
        """
        Create a new message generator thread
        @param message: Message object
        @param message_bus: MessageBus object
        @param interval: Time interval in seconds
        @param offset: Wait this time at the beginning. This prevents all
        messages to be generated at the same time (offset value is random)
        """
        threading.Thread.__init__(self)
        self.message = message            # Message to be generated
        # MessageBus where generated message is notified
        self.message_bus = message_bus
        self.interval = interval          # Time interval
        self.offset = offset              # Offset time for this thread
        self.active = True                # Keep running flag

    def run(self):
        """Start generating messages"""
        time.sleep(self.offset)
        while True:
            time.sleep(self.interval)
            if not self.active:
                break
            self.message_bus.notifyMessage(self.message)

    def stopGenerator(self):
        """Stop generating messages"""
        self.active = False

