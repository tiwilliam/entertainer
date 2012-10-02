# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''SystemTrayIcon class - Implements system tray icon for Entertainer.'''

import os

import gtk

from entertainerlib.configuration import Configuration
from entertainerlib.dialog import ManagerDialog, LogViewer


class SystemTrayIcon:
    """Implements system tray icon for entertainer."""

    FILE_DIR = os.path.dirname(__file__)
    UI_DIR = os.path.join(FILE_DIR, '..', 'uis')

    def __init__(self, quit_callback, toggle_interface_visibility_callback):
        '''Create the system tray icon and pop-up menu for it.'''
        self.quit_callback = quit_callback
        self.toggle_interface_visibility_callback = \
            toggle_interface_visibility_callback
        self.config = Configuration()

        # Path to the tray icon when using a branch
        self.tray_icon_url = os.path.join(self.FILE_DIR, "..", "..", "icons",
            "hicolor", "24x24", "apps", "entertainer.png")

        self.icon_widget = gtk.StatusIcon()
        self.icon_widget.set_tooltip(_("Entertainer Server"))

        # Load UI with gtk.Builder
        uifile = os.path.join(self.UI_DIR, 'system_tray_icon_menu.ui')
        self.menu_widgets = gtk.Builder()
        self.menu_widgets.set_translation_domain('entertainer')
        self.menu_widgets.add_from_file(uifile)

        # Bind menu signals
        callback_dic = {"on_menuitem_client_activate"
                        : self.on_menuitem_client_activate,
                        "on_menuitem_manager_activate"
                        : self.on_menuitem_manager_activate,
                        "on_menuitem_log_viewer_activate"
                        : self.on_menuitem_log_viewer_activate,
                        "on_menuitem_quit_activate"
                        : self.on_menuitem_quit_activate
                        }
        self.menu_widgets.connect_signals(callback_dic)
        self.popup = self.menu_widgets.get_object("SystemTrayIconMenu")

        # Check if running from a branch to set the tray icon
        if (os.path.exists(self.tray_icon_url)):
            self.icon_widget.set_from_file(self.tray_icon_url)
        else:
            # Must be running from a package, therefore available by icon name
            self.icon_widget.set_from_icon_name("entertainer")

        self.icon_widget.connect('activate', self.systray_icon_activated)
        self.icon_widget.connect('popup-menu', self.open_popup_menu)

    def systray_icon_activated(self, widget, data= None):
        """Switch visibility of client when system tray icon is clicked"""
        self.toggle_interface_visibility_callback()

    def open_popup_menu(self, widget, button, time, data = None):
        """Display pop-up menu when system tray icon is clicked"""
        self.popup.show_all()
        self.popup.popup(None, None, None, 3, time)

    def on_menuitem_client_activate(self, widget):
        """Execute client here if not running. Show if running"""
        self.set_client_visible(True)

    def on_menuitem_manager_activate(self, widget):
        '''Executes the manager dialog.'''
        ManagerDialog(False)

    def on_menuitem_log_viewer_activate(self, widget):
        """Display log viewer dialog"""
        LogViewer(False)

    def on_menuitem_quit_activate(self, widget):
        '''Close the application by calling the quit callback.'''
        self.quit_callback()

