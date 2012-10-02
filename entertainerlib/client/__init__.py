# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Client code for Entertainer.'''
# pylint: disable-msg=W0612

def main(*args, **kwargs):
    '''Client code main loop.'''

    # Import statements are inside the function so that they aren't imported
    # every time something from the client is imported

    # cluttergtk must be imported before the first import of clutter so it
    # must be imported even though pylint complains about it not being used.
    import cluttergtk
    import clutter
    import gobject
    import gtk

    from entertainerlib.client.translation_setup import TranslationSetup
    TranslationSetup()

    from entertainerlib.backend.backend_server import BackendServer
    from entertainerlib.configuration import Configuration
    from entertainerlib.client.client import Client

    gobject.threads_init()
    gtk.gdk.threads_init()
    clutter.threads_init()

    config = Configuration()
    if config.start_auto_server:
        print "Entertainer backend starting..."
        BackendServer()

    client_client = Client()
    client_client.start()


