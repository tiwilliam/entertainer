# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Generate translations related files, pot/po/mo'''

import glob
import os
import re
from subprocess import call
import sys

class TranslationsGenerator(object):
    '''Translation file generator'''

    def __init__(self, lib_dir = '../entertainerlib', pot_dir = 'po',
        po_dir = 'po', mo_dir = '.', exclude_dir_pattern = 'tests'):

        # Directory of python library files to search for for translations
        self.lib_dir = lib_dir

        # A directory pattern to exclude when searching
        self.exclude = exclude_dir_pattern

        # Directory where pot file is stored
        self.pot_dir = pot_dir

        # Directory where po files are stored
        self.po_dir = po_dir

        # Directory to output mo files and related directories
        self.mo_dir = mo_dir

    def update_pot(self, pot_file = 'entertainer.pot'):
        '''Update the pot file

        If the pot file does not exist, create one.
        '''

        def generate_header(ui_file):
            '''Create a header file from the ui file with intltool-extract'''

            call(['intltool-extract', '--type=gettext/glade', ui_file])

            return '%s.h' % ui_file

        # List of file names to feed to xgettext
        files_to_translate = []
        # Store header file names to clean up after pot generation is complete
        headers = []

        # Cycle through all the files and collect the necessary data
        # pylint: disable-msg=W0612
        for root, dirs, files in os.walk(self.lib_dir):
            if self.exclude in root:
                continue
            for filename in files:
                full_path = os.path.join(root, filename)

                ext = os.path.splitext(full_path)[1]
                if ext == '.py':
                    files_to_translate.append(full_path)
                elif ext == '.ui':
                    header = generate_header(full_path)
                    files_to_translate.append(header)
                    headers.append(header)

        # Generate pot file
        tmp = 'tmp.pot'
        command = ['xgettext', '--language=Python', '--keyword=_',
            '--keyword=N_', '--output=%s' % tmp]
        command.extend(files_to_translate)
        call(command)

        # Replace CHARSET with UTF-8 and write to final pot filename
        pot_path = os.path.join(self.pot_dir, pot_file)
        out = open(pot_path, 'w')
        data = open(tmp).read()
        out.write(re.sub('charset=CHARSET', 'charset=UTF-8', data))
        out.close()

        # Remove unnecessary files
        for header in headers:
            os.remove(header)
        os.remove(tmp)

    def update_pos(self, pot_file = 'entertainer.pot'):
        '''Update all po files with the data in the pot reference file.'''

        pot_path = os.path.join(self.pot_dir, pot_file)

        pos = glob.glob(os.path.join(self.po_dir, '*.po'))
        for po in pos:
            call(['msgmerge', '-U', po, pot_path])

    def update_mos(self, search_pattern = 'entertainer-(.*)\.po',
        mo_name = 'entertainer'):
        '''Generate mo files for all po files

        Search pattern is the pattern that all the po files are in. The saved
        value is the locale that is pulled out of the po filename.
        '''

        pos = glob.glob(os.path.join(self.po_dir, '*.po'))
        for po in pos:
            match = re.search(search_pattern, po)
            lang = match.group(1)
            lang_dir = '../locale/%s/LC_MESSAGES' % lang

            # Create the directory and all its intermediates if needed
            if not os.path.exists(lang_dir):
                os.makedirs(lang_dir)

            # Create the mo file from the po file
            mo_out = os.path.join(lang_dir, '%s.mo' % mo_name)
            call(['msgfmt', po, '-o', mo_out])

if __name__ == '__main__':
    translation_generator = TranslationsGenerator()

    if 'pot' in sys.argv:
        translation_generator.update_pot()
    if 'po' in sys.argv:
        translation_generator.update_pos()
    if 'mo' in sys.argv:
        translation_generator.update_mos()

