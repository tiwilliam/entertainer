# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Logger class'''

import logging

from entertainerlib.configuration import Configuration

class Logger:
    '''Logger to record behind the scenes information.

    Tailored to the liking of the Entertainer developers.'''

    def __init__(self):
        '''Create a new Entertainer logger object

        This logger creates the necessary customization for Entertainer
        logging and should be followed by a getLogger call.

        Example call:
        self.logger = Logger().getLogger('my.source.class')
        '''

        self.config = Configuration()

        logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    filename=self.config.LOG,
                    filemode='a')

    def getLogger(self, logname=''):
        '''Return a lower level logging object

        Since the low level log object does all the heavy lifting, it needs to
        be called.
        '''
        return logging.getLogger(logname)

