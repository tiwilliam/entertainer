'''A LocalServer for Entertainer.'''

from twisted.internet.protocol import ServerFactory
from twisted.protocols import amp

from entertainerlib.network.local import commands


class EntertainerLocalProtocol(amp.AMP):
    '''A local message passing protocol for Entertainer.

    This protocol should be implemented when the client and the server are on
    the same machine.
    '''

    def connectionLost(self, reason):
        '''See `twisted.protocols.Protocol.connectionLost`.'''

    def connectionMade(self):
        '''See `twisted.protocols.Protocal.connectionMade`.'''

    @commands.TenMusicTracks.responder
    def get_ten_music_tracks(self, index):
        '''Get the next ten music tracks from an index.'''
        return {'tracks': [
            {'id': 1,
            'filename': u'/foo/bar/baz',
            'title': u'Running with scissors',
            'artist': u'Teh band'},
            {'id': 1,
            'filename': u'/foo/bar/bas',
            'title': u'Fa la la',
            'artist': u'Teh band'},
        ]}


class EntertainerLocalServer(ServerFactory):
    '''A local server implementation for Entertainer.'''
    protocol = EntertainerLocalProtocol

