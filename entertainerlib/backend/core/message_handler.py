# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''MessageHandlers are registered to the MessageBus'''

class MessageHandler(object):
    """
    MessageHandler interface determines MessageBus clients.

    All objects that are interested in any messages must implement this
    interface. MessageHandlers can be registered to the MessageBus. When
    Messages occur MessageBus notifies all registered MessageHandlers.
    """

    def handleMessage(self, message):
        """
        Deriving class should implement this method.
        This method should handle incoming messages quickly. In other words,
        this function should never block or take much time to finish. Use
        threads as needed.
        @param message: Received Message object
        """
        pass

