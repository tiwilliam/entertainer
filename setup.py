#!/usr/bin/env python
# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''distutils installation script'''

from distutils.core import setup
from distutils.command.install import install as _install
import gzip
import os

from tools.translations_generator import TranslationsGenerator

# Before we build anything, create all the locales and mos from the current pos
os.chdir('tools')
translations_generator = TranslationsGenerator()
translations_generator.update_mos()
os.chdir('..')

class install(_install):
    '''Override the default install command to add some post install work.'''

    def run(self):
        '''Install does its work in the run method. Override run to add work.'''

        # Compress the man page before installing it.
        man_uncompressed = open('docs/entertainer.1', 'rb')
        man_compressed = gzip.open('docs/entertainer.1.gz', 'wb')
        man_compressed.writelines(man_uncompressed)
        man_compressed.close()
        man_uncompressed.close()

        _install.run(self)


def find_files(dirs, dest_root='share'):
    '''Walk files and directories and return them in a form for data_files.'''
    # pylint: disable-msg=W0621
    result = []
    if isinstance(dirs, str):
        dirs = [dirs]
    for directory in dirs:
        for root, dirs, files in os.walk(directory):
            dest = os.path.join(dest_root, root)
            source_files = [os.path.join(root, a_file) for a_file in files]
            result.append((dest, source_files))
    return result


entertainer_packages = []
for root, dirs, files in os.walk('entertainerlib'):
    if 'tests' in root or 'uis' in root:
        continue
    entertainer_packages.append(root)

package_data = [
    'uis/*',
    ]

data_files = find_files('cfg', 'share/entertainer')
data_files.extend(find_files('themes', 'share/entertainer'))
data_files.extend(find_files('icons'))
data_files.extend(find_files('locale'))
data_files.append(
    ('share/entertainer/docs', [
        'docs/COPYING',
        'docs/DEPENDENCIES',
        ]))
data_files.append(
    ('share/applications', ['docs/entertainer.desktop']))
data_files.append(
    ('share/man/man1', ['docs/entertainer.1.gz']))

setup(
    cmdclass={'install': install},
    name='entertainer',
    version='0.5.1',
    description='Entertainer Media Center',
    url='http://www.launchpad.net/entertainer',
    author='Entertainer Developers',
    author_email='entertainer-dev@lists.ironlionsoftware.com',
    license='GPL',
    packages=entertainer_packages,
    package_data={'entertainerlib': package_data},
    scripts=['entertainer', 'entertainer-backend', 'entertainer-manager',
        'entertainer-server'],
    data_files=data_files,
    long_description='''
        Entertainer aims to be a simple and easy-to-use media center solution
        for GNOME and Xfce desktop environments. Entertainer is written
        completely in Python using object-oriented programming paradigm.
        It uses the gstreamer multimedia framework for multimedia playback.
        The user Interface is implemented with Clutter UI-library, which
        creates sleek OpenGL animated user interfaces. Entertainer also uses
        other great projects like SQLite and iNotify for caching media
        libraries.''',
    )

