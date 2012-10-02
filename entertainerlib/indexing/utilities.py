'''Utilities used specifically by the indexer.'''
import gst

class TagGetter:
    '''A utility class for getting metadata from mp3 files.'''

    def __init__(self, filename):
        self.tags = {}

        self.pipeline = gst.parse_launch(
            'filesrc location=%(filename)s ! id3demux ! fakesink' % {
                'filename': filename})
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::tag', self.handle_bus_message_tag)
        self.pipeline.set_state(gst.STATE_PAUSED)

        while True:
            message = bus.pop()
            if not message:
                continue
            if message.type == gst.MESSAGE_TAG:
                for key in message.parse_tag().keys():
                    self.tags[key] = message.parse_tag()[key]
                break

    def handle_bus_message_tag(self, message):
        '''Handle the 'message::tag' bus message.'''
        taglist = message.parse_tag()

        for key in taglist.keys():
            self.tags[key] = taglist[key]

        #self.looping = False

    def __getattr__(self, attr):
        #TODO: handle types better
        try:
            val = self.tags[attr.replace('_', '-')]
        except KeyError:
            return None
        try:
            val = int(val)
        except ValueError:
            pass
        if type(val) == str:
            val = unicode(val)
        return val

