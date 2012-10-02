# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Configuration - Class represents Entertainer's configuration'''

import os
import shutil
import ConfigParser
from ConfigParser import NoSectionError, NoOptionError

from xdg import BaseDirectory

from entertainerlib.backend.core.message_handler import MessageHandler
from entertainerlib.backend.core.message_type_priority import MessageType
from entertainerlib.db.connection import Database
from entertainerlib.gui.theme import Theme

class Configuration(MessageHandler):
    '''Interface to all configuration parameters. All components of Entertainer
    should get configuration values through this class.'''

    _shared_state = {}

    def __init__(self, test_dir=None):
        self.__dict__ = self._shared_state
        MessageHandler.__init__(self)

        if not self._shared_state or test_dir is not None:
            # Set in a production mode or a test mode
            if test_dir is None:
                self.resources = Resources()
            else:
                self.resources = Resources(config_testing_dir=test_dir)

            self.cache_dir = self.resources.cache_dir
            self.config_dir = self.resources.config_dir
            self.data_dir = self.resources.data_dir

            self.LOG = os.path.join(self.cache_dir, u'entertainer.log')

            self.MEDIA_DB = Database(os.path.join(self.cache_dir, 'media'))

            self.IMAGE_DB = os.path.join(self.cache_dir, 'image.db')
            self.MUSIC_DB = os.path.join(self.cache_dir, 'music.db')
            self.VIDEO_DB = os.path.join(self.cache_dir, 'video.db')

            self.THUMB_DIR = os.path.join(self.cache_dir, 'thumbnails')
            self.IMAGE_THUMB_DIR = os.path.join(self.THUMB_DIR, 'image')
            self.VIDEO_THUMB_DIR = os.path.join(self.THUMB_DIR, 'video')
            self.ALBUM_ART_DIR = os.path.join(self.cache_dir, 'album_art')
            self.MOVIE_ART_DIR = os.path.join(self.cache_dir, 'movie_art')

            self.read_config_file()

            self.theme = Theme(self.theme_path)

            self._stage_width = None
            self._stage_height = None

            # Network options specify the server type and extra options
            self.network_options = {
                'type': 'local',
                'host': 'localhost',
                'port': 55545}

    def read_config_file(self):
        '''Read in the config file.'''
        self.content_conf = os.path.join(self.config_dir, 'content.conf')
        self.content = ConfigParser.ConfigParser()
        self.content.readfp(open(self.content_conf))

    def update_configuration(self):
        '''Read configuration file again and update this object.'''
        self.content.readfp(open(self.content_conf))

    def write_content_value(self, section, option, value):
        """Write a new value to the content configuration file."""

        def write_value(section, option, value):
            '''Actually write the value to the section and option.'''
            self.content.set(section, option, value)
            cfg_file = file(self.content_conf, 'w')
            self.content.write(cfg_file)

        try:
            write_value(section, option, value)
        except NoSectionError:
            # Provide an upgrade path to additions of new sections.
            shutil.rmtree(self.config_dir)
            self.resources.create_configuration()
            self.read_config_file()
            write_value(section, option, value)
        except NoOptionError:
            raise Exception("No Option to set in content.conf file")

    def _get_stage_width(self):
        '''stage_width property getter.'''
        if self._stage_width:
            return self._stage_width

        self._stage_width = self.content.getint("General", "stage_width")
        return self._stage_width

    def _set_stage_width(self, new_width):
        '''stage_width property setter.'''
        self._stage_width = new_width

    stage_width = property(_get_stage_width, _set_stage_width)

    def _get_stage_height(self):
        '''stage_height property getter.'''
        if self._stage_height:
            return self._stage_height

        self._stage_height = self.content.getint("General", "stage_height")
        return self._stage_height

    def _set_stage_height(self, new_height):
        '''stage_height property setter.'''
        self._stage_height = new_height

    stage_height = property(_get_stage_height, _set_stage_height)

    @property
    def theme_path(self):
        '''Path to the currently selected theme.'''
        theme_path = os.path.join(self.data_dir, 'themes')
        theme = self.content.get("General", "theme")
        return os.path.join(theme_path, theme)

    @property
    def tray_icon_enabled(self):
        '''Boolean to indicate whether or not to show the tray icon.'''
        return self.content.getboolean("General", "display_icon")

    @property
    def port(self):
        '''Server's port number.'''
        return self.content.getint("General", "backend_port")

    @property
    def media_folders(self):
        '''Return a list of folders for media.'''
        media = self.content.get("Media", "folders")
        return self._is_valid_media_folder(media.split(';'))

    @property
    def weather_location(self):
        '''User's weather location.'''
        return self.content.get("Weather", "location")

    @property
    def display_weather_in_client(self):
        '''Boolean to tell if weather should be displayed.'''
        return self.content.getboolean("Weather", "display_in_menu")

    @property
    def download_metadata(self):
        '''Boolean to tell if metadata should be downloaded.'''
        return self.content.getboolean("Media", "download_metadata")

    @property
    def download_album_art(self):
        '''Boolean to tell if album art should be downloaded.'''
        return self.content.getboolean("Media", "download_album_art")

    @property
    def download_lyrics(self):
        '''Boolean to tell if lyrics should be downloaded.'''
        return self.content.getboolean("Media", "download_lyrics")

    @property
    def show_effects(self):
        '''Boolean to tell if effects should be shown.'''
        return self.content.getboolean("General", "show_effects")

    @property
    def transition_effect(self):
        '''Internal name of the user's selected screen transition style.'''
        return self.content.get("General", "transition_effect")

    @property
    def theme_name(self):
        '''Name of the current theme.'''
        return self.content.get("General", "theme")

    @property
    def start_in_fullscreen(self):
        '''Boolean to determine whether to start in fullscreen mode or not.'''
        return self.content.getboolean("General", "start_in_fullscreen")

    @property
    def start_auto_server(self):
        '''Boolean to tell if the server should be auto started.'''
        return self.content.getboolean("General", "start_server_auto")

    @property
    def history_size(self):
        '''Number of screens to hold in history.'''
        return self.content.getint("General", "history_size")

    @property
    def slideshow_step(self):
        '''Amount of seconds before the slideshow steps to the next image.'''
        return self.content.getint("Photographs", "slideshow_step")

    # Implements MessageHandler interface
    def handleMessage(self, message):
        """
        Handle received messages.
        @param message: Received Message object
        """
        if message.get_type() == MessageType.CONTENT_CONF_UPDATED:
            self.update_configuration()

    def _is_valid_media_folder(self, folder_list):
        """Return a folder list where eventual cache folders are removed"""
        valid_folder_list = []

        for folder in folder_list:
            common_prefix = os.path.commonprefix([self.cache_dir, folder])
            if common_prefix != self.cache_dir:
                # if folder is not a subfolder of cache_dir, we accept it
                valid_folder_list.append(folder)

        return valid_folder_list


class Resources(object):
    '''A Wrapper for the XDG directories. Also handles creation of a new setup
    if the Entertainer directories within the XDG directories are missing. This
    class is meant solely to support Configuration and should NOT be publicly
    used because of testing conflicts that would occur.'''

    def __init__(self, resource='entertainer', config_testing_dir=None):
        if config_testing_dir is None:
            self.cache_dir = os.path.join(BaseDirectory.xdg_cache_home,
                 resource)
            self.config_dir = os.path.join(BaseDirectory.xdg_config_home,
                resource)
            self.data_dir = os.path.join(BaseDirectory.xdg_data_home, resource)
        else:
            # Running in the test suite so don't create the XDG locations.
            self.cache_dir = os.path.join(config_testing_dir, 'cache')
            self.config_dir = os.path.join(config_testing_dir, 'config')
            self.data_dir = os.path.join(config_testing_dir, 'data')

        # Ensure that the directories exist.
        if not os.path.exists(self.cache_dir):
            self.create_cache_hierarchy()
        if not os.path.exists(self.config_dir):
            self.create_configuration()
        if not os.path.exists(self.data_dir):
            self.create_initial_data()

    def create_cache_hierarchy(self):
        '''Create the cache hierarchy that is assumed to exist.'''
        os.makedirs(os.path.join(self.cache_dir, 'album_art'))
        os.makedirs(os.path.join(self.cache_dir, 'movie_art'))
        os.makedirs(os.path.join(self.cache_dir, 'thumbnails', 'image'))
        os.makedirs(os.path.join(self.cache_dir, 'thumbnails', 'video'))

    def create_configuration(self):
        '''Create the user's configuration area and populate with the default
        content configuration.'''

        # Copy configuration data from a dev branch if we can
        dev_config = os.path.abspath(os.path.dirname(__file__) + '/../cfg')
        if os.path.exists(dev_config):
            shutil.copytree(dev_config, self.config_dir)
            return

        # Must be a proper installation so install from the system location.
        installed_config = os.path.join(self.installed_data_dir, 'cfg')
        shutil.copytree(installed_config, self.config_dir)

    def create_initial_data(self):
        '''Create the initial data directory and populate with the default data
        used by Entertainer.'''
        os.mkdir(self.data_dir)

        # Copy configuration data from a dev branch if we can
        dev_config = os.path.abspath(os.path.dirname(__file__) + '/../themes')
        if os.path.exists(dev_config):
            shutil.copytree(dev_config, os.path.join(self.data_dir, 'themes'))
            return

        # Must be a proper installation so install from the system location.
        themes_dir = os.path.join(self.installed_data_dir, 'themes')
        shutil.copytree(themes_dir, os.path.join(self.data_dir, 'themes'))

    @property
    def installed_data_dir(self):
        '''Since different distros decide on the install path differently, scan
        through the system data directories to find where Entertainer was
        installed.'''

        # Get rid of the user's home data directory because we don't want it.
        system_data_dirs = [data_dir for data_dir in BaseDirectory.xdg_data_dirs
            if not data_dir.startswith(BaseDirectory.xdg_data_home)]

        installed_data_dir = None
        for directory in system_data_dirs:
            possible_data_dir = os.path.join(directory, 'entertainer')
            if os.path.exists(possible_data_dir):
                installed_data_dir = possible_data_dir
                break

        return installed_data_dir

