# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Backend component protocol for communicating'''

class Message:
    """
    Backend components uses Messages to communicate with each other.

    Message has two internal data fields: type and data. Type determines what
    kind of message this is. MessageHandlers can read type with get_type()
    method and act differently on different messages. Message can also include
    extra data object, but ths is optional. MessageHandler can get data with
    get_date() method.
    """

    def __init__(self, message_type, message_data = None):
        """
        Create a new Message object with given type and data
        """
        # MessageHandlers use this to detect message's type.
        self.message_type = message_type
        # Message data object. Messages can contain extra data.
        self.message_data = message_data

    def get_type(self):
        """
        Get message type
        @return: Message type as integer (see message_type_priority.py)
        """
        return self.message_type

    def get_data(self):
        """
        Get message data. Return None if there is no data
        @return: Userdata or None if there data is not set
        """
        return self.message_data

