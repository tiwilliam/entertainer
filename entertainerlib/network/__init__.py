'''Network functionality for Entertainer.'''
import sys

from twisted.internet import reactor
from twisted.python.log import startLogging

from entertainerlib.configuration import Configuration
from entertainerlib.network.local.server import EntertainerLocalServer


# New server types must be registered here.
server_registry = {
    'local': EntertainerLocalServer}

# Entertainer really needs a good absctractable way to handle command line
# arguments.
def server_main(*args, **kwargs):
    '''Entertainer Server main function.'''
    startLogging(sys.stdout)
    config = Configuration()
    server = server_registry.get(
        config.network_options['type'])

    server = server()
    reactor.listenTCP(config.network_options['port'], server)
    reactor.run()

