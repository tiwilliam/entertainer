# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Test MessageType'''

from entertainerlib.backend.core.message_type_priority import MessageType
from entertainerlib.tests import EntertainerTest

class TestMessageType(EntertainerTest):
    """Test MessageType"""

    def setUp(self):
        """Set up test"""
        self.NUMBER_OF_MESSAGE_TYPES = len(
        [k for k, v in vars(MessageType).items() if type(v) is int]
        )
        EntertainerTest.setUp(self)

    def tearDown(self):
        """Tear down test"""
        EntertainerTest.tearDown(self)

    def testProperSequence(self):
        """
        testProperSequence: Tests whether the ids for message types are in the
        correct sequence. ie if there are 17 types the ids should be 
        consecutive numbers between 0 and 16
        """
        type_numbers = []
        for v in vars(MessageType).items():
            if type(v[1]) is int:
                type_numbers.append(v[1])
        type_numbers.sort()
        for i in range(self.NUMBER_OF_MESSAGE_TYPES):
            self.assertEqual(i, type_numbers[i])
