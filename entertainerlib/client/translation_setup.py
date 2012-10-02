# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Translation Setup Code'''

import gettext
import locale
import os

from xdg import BaseDirectory

class TranslationSetup:
    def __init__(self):
        '''Because of how early translation setup has to occur. This should be
        the only file outside of Configuration that imports xdg.'''

        def install_locale(locale_dir):
            '''Install locale data from the provided directory.'''
            # This sets up the _ function
            gettext.install('entertainer', localedir=locale_dir,
                    unicode=True)
            # Call the C library gettext functions and set the codeset
            # to avoid locale-dependent translation of the message catalog
            locale.bindtextdomain('entertainer', locale_dir)
            locale.bind_textdomain_codeset('entertainer', "UTF-8")
            # XXX: fmarl - setlocale load in current locale properly
            # We can remove it and get feedback from users to see if
            # this hack it's really needed.
            try:
                locale.setlocale(locale.LC_ALL, "")
            except locale.Error:
                pass

        # Find locale data from a dev branch if we can
        dev_locale =  os.path.abspath(os.path.dirname(__file__) +
           '/../../locale')
        if os.path.exists(dev_locale):
            install_locale(dev_locale)

        # Install locale data from the system location
        else:
            system_data_dirs = [data_dir for data_dir in
                BaseDirectory.xdg_data_dirs if not
                data_dir.startswith(BaseDirectory.xdg_data_home)]
            # Since we don't know for certain where the mo files were installed,
            # we try to install from both /usr/share and /usr/local/share.
            for data_dir in system_data_dirs:
                system_locale = os.path.join(data_dir, 'locale')
                install_locale(system_locale)
