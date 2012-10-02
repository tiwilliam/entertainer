'''Local network protocol commands.'''
from twisted.protocols import amp

class TenMusicTracks(amp.Command):
    arguments = [('index', amp.Integer())]
    response = [
        ('tracks', amp.AmpList([
            ('id', amp.Integer()),
            ('filename', amp.Unicode()),
            ('title', amp.Unicode()),
            ('artist', amp.Unicode())]
        ))]


