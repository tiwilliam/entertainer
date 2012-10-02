# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests Configuration'''
# pylint: disable-msg=W0212

import os

from entertainerlib.tests import EntertainerTest
from entertainerlib.configuration import Configuration

class ConfigurationTest(EntertainerTest):
    '''Test for utils.configuration'''

    def setUp(self):
        '''Set up the test'''
        EntertainerTest.setUp(self)

        self.configuration = Configuration()

    def test_create(self):
        '''Test correct Configuration initialization.'''
        self.assertTrue(isinstance(self.configuration, Configuration))
        self.assertEqual(self.configuration.config_dir,
            os.path.join(self.test_cfg_dir, 'config'))
        self.assertEqual(self.configuration.theme_path,
            os.path.join(self.test_cfg_dir, 'data', 'themes', 'Default'))
        self.assertFalse(self.configuration.tray_icon_enabled)
        self.assertEqual(self.configuration.port, 45054)
        self.assertEqual(self.configuration.media_folders, [''])
        self.assertEqual(self.configuration.weather_location, 'Bath,England')
        self.assertTrue(self.configuration.display_weather_in_client)
        self.assertTrue(self.configuration.download_metadata)
        self.assertTrue(self.configuration.download_album_art)
        self.assertFalse(self.configuration.download_lyrics)
        self.assertTrue(self.configuration.show_effects)
        self.assertEqual(self.configuration.transition_effect, 'Slide')
        self.assertEqual(self.configuration.theme_name, 'Default')
        self.assertTrue(self.configuration.start_in_fullscreen)
        self.assertTrue(self.configuration.start_auto_server)
        self.assertEqual(self.configuration.history_size, 8)
        self.assertEqual(self.configuration.slideshow_step, 5)

    def test_create_dir(self):
        '''Test Configuration object directory creation'''
        self.assertTrue(os.path.exists(self.test_cfg_dir))

    def testBorg(self):
        '''Test that configuration objects share state'''
        self.second_config = Configuration()
        self.assertTrue(
            self.second_config.__dict__ is self.configuration.__dict__)

    def test_stage_width(self):
        '''Test the stage_width property.'''
        self.assertEqual(self.configuration.stage_width, 1366)
        self.configuration.stage_width = 1600
        self.assertEqual(self.configuration.stage_width, 1600)

    def test_stage_height(self):
        '''Test the stage_height property.'''
        self.assertEqual(self.configuration.stage_height, 768)
        self.configuration.stage_height = 900
        self.assertEqual(self.configuration.stage_height, 900)

    def test_write_content_value(self):
        """Test writing a value to the content configuration file"""
        new_value = "Gaithersburg,Maryland"
        self.configuration.write_content_value("Weather", "location", new_value)
        self.configuration.update_configuration()
        self.assertEqual(self.configuration.weather_location, new_value)

