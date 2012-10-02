'''Classes to produce a local storage implementation.'''
# pylint: disable-msg=W0223

#from twisted.internet.defer import inlineCallbacks
from twisted.protocols import amp

#from entertainerlib.network.local.commands import TenMusicTracks
from entertainerlib.network.storage import Storage


class EntertainerLocalClientProtocol(amp.AMP):
    '''The client protocol to communicate with the local server.'''

    def connectionMade(self):
        '''See `twisted.protocols.Protocal.connectionMade`.'''
        self.get_ten_tracks(1)

#    @inlineCallbacks
#    def get_ten_tracks(self, index):
#        '''Get ten tracks starting with the given index.'''
#        result = yield self.callRemote(TenMusicTracks, index=index)
#        print result


class LocalStorage(Storage):
    '''A local storage implementation.'''

    def __init__(self):
        Storage.__init__(self)
        self.protocol = EntertainerLocalClientProtocol
        self.host = 'localhost'
        # TODO: This port number could probably be a config var.
        self.port = 5545


