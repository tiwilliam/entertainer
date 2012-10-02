# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Playlist - Playlist class is a simple container for Playable objects'''

import random

class Playlist(object):
    """
    Playlist

    List contains a group of playables that are played by MediaPlayer object.
    Playlist allows removing and adding items dynamically. Client can query
    next, previous and random playable from playlist. Playlist internally
    updates pointer that keeps track on current position.
    """

    def __init__(self, playables=None):
        """
        Intialize playlist
        @param playables: List of Playable objects
        """
        self.list = playables
        if playables is None:
            self.list = []

        self.position = 0

    def add(self, playable):
        """
        Add new playable to this playlist.
        @param playable: Object that implements Playable interface
        """
        self.list.append(playable)

    def remove(self, playable):
        """
        Remove playable from this playlist
        @param playable: Object that implements Playable interface
        """
        self.remove(playable)
        if self.position == len(self.list):
            self.position = len(self.list) -1

    def set_current(self, index):
        """
        Set pointer inside playlist to some spesific index. Index must be
        non-negative and smaller than playlist length.
        @param index: Integer - wanted index
        """
        if index >= 0 and index < len(self.list):
            self.position = index
        else:
            raise Exception("Playlist pointer: Index out of bounds")

    def has_next(self):
        """
        Is there next track on this play list.
        @return: boolean
        """
        if self.position == len(self.list) - 1:
            return False
        else:
            return True

    def has_previous(self):
        """
        Is there previous track on this play list.
        @return: boolean
        """
        if self.position == 0:
            return False
        else:
            return True

    def get_next(self):
        """
        Return next playable from the playlist. This method also moves
        pointer inside playlist.
        @return: Playable object
        """
        if self.has_next():
            self.position = self.position + 1
            return self.list[self.position]
        else:
            raise Exception("Next track doesn't exist")

    def get_previous(self):
        """
        Return next playable from the playlist. This method also moves
        pointer inside playlist.
        @return: Playable object
        """
        if self.has_previous():
            self.position = self.position - 1
            return self.list[self.position]
        else:
            raise Exception("Previous track doesn't exist")

    def get_current(self):
        """
        Return current playable form playlist.
        @return: Playable object
        """
        return self.list[self.position]

    def get_random(self):
        """
        Return random playable form playlist. Also moves pointer to returned
        item.
        @return: Playable object
        """
        self.position = random.randint(0, len(self.list) - 1)
        return self.list[self.position]

    def get_number_of_items(self):
        """
        Get number of items on this playlist.
        @return: Integer
        """
        return len(self.list)

    def __len__(self):
        """Override len method for this type"""
        return len(self.list)

    def get_item_from_position(self, position):
        """
        Get spesific item from playlist. This method moves internal pointer
        to requested item.
        @return: Playable object
        """
        if position >= 0 and position < len(self.list):
            self.position = position
            return self.list[self.position]
        else:
            raise Exception("Position out of boundaries!")

