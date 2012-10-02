# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''UserEvent - Event generated by user action.'''

class UserEvent:
    """
    UserEvent object wraps one event.

    These event objects are created when user input is received from keyboard,
    remote control or possibly from some other input device. This class is a
    simple abstraction for all input actions. It's purpose is to hide input
    device specific stuff from rest of the user interface.
    """

    # Player events
    PLAYER_PLAY_PAUSE = 0
    PLAYER_STOP = 1
    PLAYER_NEXT = 2
    PLAYER_PREVIOUS = 3
    PLAYER_SKIP_FORWARD = 4
    PLAYER_SKIP_BACKWARD = 5
    PLAYER_VOLUME_UP = 6
    PLAYER_VOLUME_DOWN = 7

    # Navigation events
    NAVIGATE_UP = 20
    NAVIGATE_DOWN = 21
    NAVIGATE_LEFT = 22
    NAVIGATE_RIGHT = 23
    NAVIGATE_HOME = 24
    NAVIGATE_BACK = 26
    NAVIGATE_SELECT = 27
    NAVIGATE_NEXT_PAGE = 29
    NAVIGATE_PREVIOUS_PAGE = 30
    NAVIGATE_FIRST_PAGE = 31
    NAVIGATE_LAST_PAGE = 32

    # Other events
    TOGGLE_FULLSCREEN = 50
    USE_ASPECT_RATIO_1 = 51
    USE_ASPECT_RATIO_2 = 52
    USE_ASPECT_RATIO_3 = 53
    USE_ASPECT_RATIO_4 = 54
    QUIT = 56
    DEFAULT_EVENT = 57

    def __init__(self, code):
        """
        Create a new UserEvent object.
        @param code: One of the event codes defined in the UserEvent class.
        """
        self.code = code

    def get_type(self):
        """
        Get event type code. These codes are defined in this class.
        @return: Integer, type code
        """
        return self.code
