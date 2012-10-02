# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Transition - All transition effects has to implement this interface!'''

class Transition:
    """
    Transition interface

    All transition effects has to implement this interface! Transition
    implements effect that is used between screen chanages. This can for
    example fade, slide, zoom, etc.
    """

    # These constants specify the direction of the screen change.
    FORWARD = 0
    BACKWARD = 1

    def __init__(self, remove_from_stage_callback):
        '''Initialize transition effect.'''
        self.remove_from_stage_callback = remove_from_stage_callback
        self.direction = self.FORWARD # Default direction

    def forward_effect(self, from_screen, to_screen):
        '''
        Animate transition from 'from_screen' to 'to_screen'. This function
        should remove "from_screen" textures and widgets from view and add
        "to_screen" widgets and other stuff to view. While doing this it
        should look nice. Notice that 'from_screen' is None when the Main screen
        is displayed at the first time. Eg. when application starts up.
        '''
        pass

    def backward_effect(self, from_screen, to_screen):
        '''
        Animate transition from 'from_screen' to 'to_screen'. This function
        should remove "from_screen" textures and widgets from canvas and add
        "to_screen" widgets and other stuff to canvas. While doing this it
        should look nice. THIS IS CALLED WHEN USER HITS 'BACK' BUTTON. Usually
        it looks good and logical if animation is done backwards. This gives
        the feel of getting back to the previous screen.
        '''
        pass

    def _remove_from_stage_callback(self, timeline, screen):
        '''
        Callback for backward_effect timeline. This method is called when
        transition direction is BACKWARDS. This method delegates to the method
        provided when the transition was created.
        '''
        self.remove_from_stage_callback(screen)

