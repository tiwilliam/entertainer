# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Dialogs for Entertainer.'''
# pylint: disable-msg=C0302

import os
import shutil
import socket
import sys
import tarfile

import gtk

from entertainerlib.backend.core.message import Message
from entertainerlib.backend.core.message_bus_proxy import MessageBusProxy
from entertainerlib.backend.core.message_type_priority import MessageType
from entertainerlib.configuration import Configuration
from entertainerlib.logger import Logger
from entertainerlib.gui.theme import Theme
from entertainerlib.weather import Weather


class ManagerDialog:
    """
    This is a content management tool for Entertainer media center application.
    """

    # Temporary storage for entered URL
    url = ""
    UI_DIR = os.path.join(os.path.dirname(__file__), "uis")

    def __init__(self, stand_alone):
        """
        Initialize content management dialog
        @param stand_alone: Boolean, Is this dialog running as a stand alone
            process
        """
        self.stand_alone = stand_alone
        self.config = Configuration()
        self.themes = []
        self.weather = Weather()

        # Load UI with gtk.Builder
        uifile = os.path.join(self.UI_DIR, 'manager.ui')
        self.builder = gtk.Builder()
        self.builder.set_translation_domain('entertainer')
        self.builder.add_from_file(uifile)

        # Get content management dialog and bind signal callbacks
        self.dialog = self.builder.get_object("ManagerDialog")
        if (self.dialog):
            callback_dic = {
                # Dialog-wide callbacks
                "on_close_button_clicked" : self.on_close_button_clicked,
                "on_ManagerDialog_destroy" : self.on_dialog_closed,

                # Media tab
                "on_button_remove_media_clicked" :
                    self.on_button_remove_media_clicked,
                "on_button_add_media_clicked" :
                    self.on_button_add_media_clicked,
                "on_button_edit_media_clicked" :
                    self.on_button_edit_media_clicked,
                "on_checkbutton_video_metadata_toggled" :
                    self.on_checkbutton_video_metadata_toggled,
                "on_lyrics_checkbox_toggled" : self.on_lyrics_checkbox_toggled,
                "on_art_checkbox_toggled" : self.on_art_checkbox_toggled,
                "on_button_media_rebuild_clicked" :
                    self.on_button_media_rebuild_clicked,

                # Weather tab
                "on_button_add_weather_clicked" :
                    self.on_button_add_weather_clicked,
                "on_button_remove_weather_clicked" :
                    self.on_button_remove_weather_clicked,
                "on_weather_display_checkbox_toggled" :
                    self.on_weather_display_checkbox_toggled,
                "on_location_find_button_clicked" :
                    self.on_location_find_button_clicked,
                "on_location_cancel_button_clicked" :
                    self.on_location_cancel_button_clicked,
                "on_location_add_button_clicked" :
                    self.on_location_add_button_clicked,
                "on_location_entry_activate" : self.on_location_entry_activate,

                # User Interface tab
                "on_theme_list_cursor_changed" :
                    self.on_theme_list_cursor_changed,
                "on_theme_add_button_clicked" :
                    self.on_theme_add_button_clicked,
                "on_theme_remove_button_clicked" :
                    self.on_theme_remove_button_clicked,
                "on_checkbutton_effects_toggled" :
                    self.on_checkbutton_effects_toggled,
                "on_combobox_effects_changed" :
                    self.on_combobox_effects_changed,

                # General tab
                "on_checkbutton_fullscreen_toggled" :
                    self.on_checkbutton_fullscreen_toggled,
                "on_checkbutton_autostart_toggled" :
                    self.on_checkbutton_autostart_toggled,
                "on_checkbutton_systray_icon_toggled" :
                    self.on_checkbutton_systray_icon_toggled,
                "on_spinbutton_slideshow_step_value_changed":
                    self.on_spinbutton_slideshow_step_value_changed
                }

        self.builder.connect_signals(callback_dic)

        # Initialize dialog widgets with correct values and show dialog
        self.init_dialog_values_from_configure_file()
        self.dialog.resize(500, 300)
        self.dialog.show()

        # Initialize location list in search dialog
        result_list = self.builder.get_object("location_results_treeview")
        store = gtk.ListStore(str)
        result_list.set_model(store)
        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Location"), cell_renderer, text=0)
        result_list.append_column(column)

    def on_dialog_closed(self, widget):
        """Callback function for dialog's close button"""
        try:
            proxy = MessageBusProxy(client_name = "Manager GUI")
            proxy.connectToMessageBus()
            proxy.sendMessage(Message(MessageType.CONTENT_CONF_UPDATED))
            proxy.disconnectFromMessageBus()
        except socket.error:
            error = gtk.MessageDialog(
                    None, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _(
                        "Entertainer backend is not running. "
                        "Cache cannot be rebuilt."
                    ))
            error.run()
            error.destroy()

        if(self.stand_alone):
            self.dialog.hide()
            self.dialog.destroy()
            gtk.main_quit()
        else:
            self.dialog.hide()
            self.dialog.destroy()

    def on_close_button_clicked(self, widget):
        """Callback function for dialog's close button"""
        if(self.stand_alone):
            self.dialog.hide()
            self.dialog.destroy()
            gtk.main_quit()
        else:
            self.dialog.hide()
            self.dialog.destroy()

    def on_button_add_media_clicked(self, widget):
        """Opens add URL dialog. """
        widget = self.builder.get_object("treeview_media")
        model = widget.get_model()
        # Open "Select folder" dialog
        dialog =  gtk.FileChooserDialog(_("Select folder"), None,
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,gtk.RESPONSE_OK),
            None)
        status = dialog.run()
        # If folder was selected we add it to model and update config file
        if(status == gtk.RESPONSE_OK):
            self.add_to_model_and_config(dialog.get_current_folder(), model,
                self.media_folders, "Media")
        dialog.destroy()

    def on_button_remove_media_clicked(self, widget):
        """Remove currently selected folder from media folders"""
        widget = self.builder.get_object("treeview_media")
        model = widget.get_model()
        selection = widget.get_selection().get_selected()
        if selection[1] == None:
            return
        rm_folder = model.get_value(selection[1], 0)
        self.media_folders.remove(rm_folder)
        str_folders = ";".join(self.media_folders)
        self.config.write_content_value("Media", "folders", str_folders)
        model.remove(selection[1])

    def on_button_edit_media_clicked(self, widget):
        """Edit currently selected folder"""
        widget = self.builder.get_object("treeview_media")
        url_dialog = self.builder.get_object("url_dialog")
        url_entry = self.builder.get_object("url_entry")
        model = widget.get_model()
        selection = widget.get_selection().get_selected()
        if selection[1] == None:
            return
        folder = model.get_value(selection[1], 0)
        url_entry.set_text(folder)
        url_dialog.set_title(_("Edit URL"))
        status = url_dialog.run()
        if status == gtk.RESPONSE_OK and os.path.exists(self.url):
            # Update list model
            model.set_value(selection[1], 0, self.url)
            # Update configure file
            pos = self.media_folders.index(folder)
            self.media_folders.remove(folder)
            self.media_folders.insert(pos, self.url)
            str_folders = ";".join(self.media_folders)
            self.config.write_content_value("Media", "folders",
                str_folders)

    def on_checkbutton_autostart_toggled(self, widget):
        '''Server autostart checkbox toggled.'''
        self.config.write_content_value("General", "start_server_auto",
            widget.get_active())

    def on_checkbutton_fullscreen_toggled(self, widget):
        '''Start in fullscreen checkbox toggled.'''
        self.config.write_content_value("General", "start_in_fullscreen",
            widget.get_active())

    def on_checkbutton_systray_icon_toggled(self, widget):
        """System Tray Icon checkbox toggled"""
        self.config.write_content_value("General", "display_icon",
            widget.get_active())

    def on_checkbutton_video_metadata_toggled(self, widget):
        """
        Download video file metadata from internet
        @param widget: GTK-Widget
        """
        self.config.write_content_value("Media", "download_metadata",
            widget.get_active())

    def on_spinbutton_slideshow_step_value_changed(self, widget):
        """Activation of slideshow effects"""
        self.config.write_content_value("Photographs", "slideshow_step",
            int(widget.get_value()))

    def on_lyrics_checkbox_toggled(self, widget):
        self.config.write_content_value("Media", "download_lyrics",
            widget.get_active())

    def on_art_checkbox_toggled(self, widget):
        self.config.write_content_value("Media", "download_album_art",
            widget.get_active())

    def on_button_add_weather_clicked(self, widget):
        """
        Open location search dialog
        @param widget: GTK-Widget
        """
        location_dialog = self.builder.get_object("weather_search_dialog")
        location_dialog.set_title(_("Add location"))

        # Clear results
        result_list = self.builder.get_object("location_results_treeview")
        model = result_list.get_model()
        model.clear()

        status = location_dialog.run()
        if(status == gtk.RESPONSE_OK):
            print "Added"

    def on_button_remove_weather_clicked(self, widget):
        """
        Remove currently selected weather location from the location list
        @param widget: GTK-Widget
        """
        widget = self.builder.get_object("treeview_locations")
        model = widget.get_model()
        self.weather_locations = []
        str_folders = ""
        self.config.write_content_value("Weather", "location", str_folders)
        model.clear()

    def on_weather_display_checkbox_toggled(self, widget):
        """
        Checkbox that defines should we use weather conditions
        @param widget: GTK-Widget
        """
        self.config.write_content_value("Weather", "display_in_menu",
            widget.get_active())
        if widget.get_active():
            self.builder.get_object("button_add_weather").set_sensitive(True)
            self.builder.get_object(
                "button_remove_weather").set_sensitive(True)
            self.builder.get_object("treeview_locations").set_sensitive(True)
        else:
            self.builder.get_object("button_add_weather").set_sensitive(False)
            self.builder.get_object(
                "button_remove_weather").set_sensitive(False)
            self.builder.get_object("treeview_locations").set_sensitive(False)

    def on_location_find_button_clicked(self, widget):
        """
        Find location by search string
        @param widget: GTK-Widget
        """
        add_button = self.builder.get_object("location_add_button")
        search_term = self.builder.get_object("location_entry").get_text()
        result_list = self.builder.get_object("location_results_treeview")
        model = result_list.get_model()
        model.clear()
        if search_term != "":
            self.weather.location = search_term
            self.weather.refresh()
            results = self.weather.forecasts
            if len(results) > 0:
                add_button.set_sensitive(True)
                model.append([search_term])
                result_list.set_cursor(0)
            else:
                model.clear()
                model.append([_("Location Not Found!")])
                add_button.set_sensitive(False)

    def on_location_cancel_button_clicked(self, widget):
        """
        Close location search dialog without taking any actions.0
        @param widget: GTK-Widget
        """
        location_dialog = self.builder.get_object("weather_search_dialog")
        location_entry = self.builder.get_object("location_entry")
        location_dialog.hide()
        location_entry.set_text("")
        location_dialog.response(gtk.RESPONSE_CANCEL)

    def on_location_add_button_clicked(self, widget):
        """
        Add selected location to location list and close search dialog
        @param widget: GTK-Widget
        """
        self.weather_locations = []
        result_list = self.builder.get_object("location_results_treeview")
        model = result_list.get_model()
        selection = result_list.get_selection().get_selected()
        if selection[1] == None:
            return
        location_string = model.get_value(selection[1], 0)

        location_list = self.builder.get_object("treeview_locations")
        loc_model = location_list.get_model()
        loc_model.clear()
        loc_model.append([location_string])

        self.weather_locations.append(location_string)
        str_locations = ";".join(self.weather_locations)
        self.config.write_content_value("Weather", "location", str_locations)

        location_dialog = self.builder.get_object("weather_search_dialog")
        location_entry = self.builder.get_object("location_entry")
        location_dialog.hide()
        location_entry.set_text("")
        location_dialog.response(gtk.RESPONSE_CANCEL)

    def on_location_entry_activate(self, widget):
        """
        User hit enter on location entry to start search
        @param widget: GTK-Widget
        """
        self.on_location_find_button_clicked(widget)

    def on_button_media_rebuild_clicked(self, widget):
        '''Rebuild media cache requested.'''
        try:
            proxy = MessageBusProxy(client_name = "Manager GUI")
            proxy.connectToMessageBus()
            proxy.sendMessage(Message(MessageType.REBUILD_IMAGE_CACHE))
            proxy.sendMessage(Message(MessageType.REBUILD_MUSIC_CACHE))
            proxy.sendMessage(Message(MessageType.REBUILD_VIDEO_CACHE))
            proxy.disconnectFromMessageBus()
        except socket.error:
            error = gtk.MessageDialog(
                None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _(
                    "Entertainer backend is not running. "
                    "Cache cannot be rebuilt."
                ))
            error.run()
            error.destroy()

    def on_theme_add_button_clicked(self, widget):
        """Add theme button clicked"""
        themelist = self.builder.get_object("theme_list")
        model = themelist.get_model()
        # Open "Select folder" dialog
        dialog = gtk.FileChooserDialog(_("Select theme package file"),
            None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), None)
        file_filter = gtk.FileFilter()
        file_filter.set_name(_("Theme package (tar.gz)"))
        file_filter.add_pattern("*.tar.gz")
        dialog.add_filter(file_filter)
        status = dialog.run()

        # If theme was selected with file chooser
        if(status == gtk.RESPONSE_OK):
            package = dialog.get_filename()
            tar = tarfile.open(package, 'r:gz') # Open tar.gz package

            # Make sure that package contains configuration file (is theme)
            content = tar.getnames()
            theme_name = None
            is_theme = False
            for element in content:
                if element[-10:] == "theme.conf":
                    theme_name = element[:-11]
                    is_theme = True

            # Install them
            if is_theme:
                tar.extractall(os.path.join(self.config.data_dir, 'themes'))
                model.insert(len(model), [theme_name])
            else:
                error = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Invalid theme file!"))
                error.run()
                error.destroy()

        dialog.destroy()

    def on_theme_list_cursor_changed(self, widget):
        """Executed when theme is changed in theme list. Update preview."""
        # Get currently selected theme
        themelist = self.builder.get_object("theme_list")
        model = themelist.get_model()
        selection = themelist.get_selection().get_selected()
        name = model.get_value(selection[1], 0)
        themedir = os.path.join(self.config.data_dir, 'themes', name)
        theme = Theme(theme_path=themedir)

        # Update preview
        image = self.builder.get_object("theme_image")
        image.set_from_file(os.path.join(themedir, "thumbnail.png"))
        name = self.builder.get_object("name_label")
        name.set_text(theme.getName())
        author = self.builder.get_object("author_label")
        author.set_text(theme.getAuthor())
        license_label = self.builder.get_object("license_label")
        license_label.set_text(theme.getLicence())
        copyright_label = self.builder.get_object("copyright_label")
        copyright_label.set_text(theme.getCopyright())
        comment = self.builder.get_object("comment_label")
        comment.set_text(theme.getComment())

        self.config.write_content_value("General", "theme", name.get_text())

    def on_theme_remove_button_clicked(self, widget):
        """Remove theme button clicked"""
        # Get currently selected theme
        themelist = self.builder.get_object("theme_list")
        model = themelist.get_model()
        selection = themelist.get_selection().get_selected()
        name = model.get_value(selection[1], 0)

        confirm = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                _("Are you sure you want to delete\ntheme: %(name)s") % \
                {'name': name})
        status = confirm.run()
        confirm.destroy()
        if(status == gtk.RESPONSE_YES):
            themedir = os.path.join(self.config.data_dir, 'themes', name)
            shutil.rmtree(themedir)
            model.remove(selection[1])
            themelist.set_cursor(0)
            self.themes.remove(name)

    def on_checkbutton_effects_toggled(self, widget):
        """Effect checkbox toggled"""
        combobox = self.builder.get_object("combobox_effects")
        combobox.set_sensitive(widget.get_active())
        self.config.write_content_value("General", "show_effects",
            widget.get_active())

    def on_combobox_effects_changed(self, widget):
        """User changed effect for screen transitions"""
        text = widget.get_active_text()
        if text == _("No effect"):
            english_text = "No effect"
        if text == _("Crossfade"):
            english_text = "Crossfade"
        if text == _("Zoom and fade"):
            english_text = "Zoom and fade"
        if text == _("Slide"):
            english_text = "Slide"
        self.config.write_content_value("General", "transition_effect",
            english_text)

    def init_dialog_values_from_configure_file(self):
        """Read configuration and set dialog widget values with read values.
        """
        # == Videos ==
        medialist_widget = self.builder.get_object("treeview_media")
        mediastore = gtk.ListStore(str)

        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Folders"), cell_renderer, text=0)
        medialist_widget.append_column(column)

        self.media_folders = self.config.media_folders

        # Fill model with folders read from config file
        self.init_model(mediastore, self.media_folders)

        medialist_widget.set_model(mediastore)

        # Checkboxes
        metadata_checkbox = self.builder.get_object("video_metadata_checkbox")
        metadata_checkbox.set_active(self.config.download_metadata)

        art_checkbox = self.builder.get_object("art_checkbox")
        art_checkbox.set_active(self.config.download_album_art)

        lyrics_checkbox = self.builder.get_object("lyrics_checkbox")
        lyrics_checkbox.set_active(self.config.download_lyrics)

        # == Weather ==
        locationlist_widget = self.builder.get_object("treeview_locations")
        location_model = gtk.ListStore(str)

        loc_cell = gtk.CellRendererText()
        location_column = gtk.TreeViewColumn(_("Location"), loc_cell, text=0)
        locationlist_widget.append_column(location_column)

        self.weather_location = self.config.weather_location

        # Fill model with location read from config file
        location_model.insert(0, [self.weather_location])
        locationlist_widget.set_model(location_model)

        weather_display_checkbox = self.builder.get_object(
            "weather_display_checkbox")
        display_val = self.config.display_weather_in_client
        weather_display_checkbox.set_active(display_val)
        if not display_val:
            self.builder.get_object("button_add_weather").set_sensitive(False)
            self.builder.get_object("button_remove_weather").set_sensitive(
                False)
            self.builder.get_object("treeview_locations").set_sensitive(False)

        # == User Interface ==
        self.load_themes()
        current_theme = self.config.theme_name

        themelist_widget = self.builder.get_object("theme_list")
        model = gtk.ListStore(str)

        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Themes", cell_renderer, text=0)
        themelist_widget.append_column(column)

        # Fill model with installed themes
        for i in range(len(self.themes)):
            model.insert(i, [self.themes[i]])

        themelist_widget.set_model(model)

        # Set current theme selected in theme list
        index = model.get_iter_first()
        unselected = True
        index_counter = 0
        while(unselected):
            name = model.get_value(index, 0)
            if name == current_theme:
                unselected = False
                themelist_widget.set_cursor(index_counter)
            index = model.iter_next(index)
            index_counter += 1

        effect_checkbox = self.builder.get_object("checkbutton_effects")
        effect_combobox = self.builder.get_object("combobox_effects")
        if self.config.show_effects:
            effect_checkbox.set_active(True)
            effect_combobox.set_sensitive(True)
        else:
            effect_checkbox.set_active(False)
            effect_combobox.set_sensitive(False)

        # Set Effect Combobox value (Text values are set in ui file)
        effect = self.config.transition_effect
        if effect == "No effect":
            effect_combobox.set_active(0)
        if effect == "Crossfade":
            effect_combobox.set_active(1)
        if effect == "Zoom and fade":
            effect_combobox.set_active(2)
        if effect == "Slide":
            effect_combobox.set_active(3)

        # == General ==
        checkbutton_fullscreen = self.builder.get_object(
            "checkbutton_fullscreen")
        if self.config.start_in_fullscreen:
            checkbutton_fullscreen.set_active(True)
        else:
            checkbutton_fullscreen.set_active(False)

        checkbutton_autostart = self.builder.get_object("checkbutton_autostart")
        if self.config.start_auto_server:
            checkbutton_autostart.set_active(True)
        else:
            checkbutton_autostart.set_active(False)

        checkbutton_systray_icon = self.builder.get_object(
            "checkbutton_systray_icon")
        if self.config.tray_icon_enabled:
            checkbutton_systray_icon.set_active(True)
        else:
            checkbutton_systray_icon.set_active(False)

        spinbutton_slideshow_step = self.builder.get_object(
            "spinbutton_slideshow_step")
        spinbutton_slideshow_step.set_value(self.config.slideshow_step)

    def add_to_model_and_config(self, selected_folder, model, folders, kind):
        """
        Add selected_folder to the model and the folders list while updating
        the configuration item section specified by type
        """
        if not selected_folder in folders:
            model.append([selected_folder])

            if(folders == None):
                folders = [selected_folder]
            else:
                folders.append(selected_folder)

            if "" in folders:
                folders.remove("")
            str_folders = ";".join(folders)
            self.config.write_content_value(kind, "folders", str_folders)

    def init_model(self, model, items):
        """Fill model with items from supplied list"""
        for i in range(len(items)):
            if not str(items[i]).strip() == "":
                model.insert(i, [items[i]])

    def load_themes(self):
        """Load themes"""
        themes = os.listdir(os.path.join(self.config.data_dir, 'themes'))
        for element in themes:
            theme = os.path.join(self.config.data_dir, 'themes', element)
            if os.path.isdir(theme):
                self.themes.append(element)


class LogViewer:
    """
    Implements dialog that allows user to see logged events.

    This dialog is used to check Entertainer logfiles. It reads all data from
    selected file and saves rows to self.log_rows. Then it filters unwanted
    rows away by calling self.filterMessages(). This method adds rows to
    ListStore, which is the model of TreeView object.

    Combobox and refresh -button actions read files again
    Checkbox actions just filter current rows again
    """

    UI_DIR = os.path.join(os.path.dirname(__file__), "uis")

    # Is this dialog running as a stand alone process
    __STAND_ALONE = None

    widgets = None
    dialog = None
    log_store = None
    log_rows = []

    def __init__(self, stand_alone):
        self.logfile_entertainer = Configuration().LOG
        self.logger = Logger().getLogger('utils.log_viewer')

        self.__STAND_ALONE = stand_alone
        try:
            uifile = os.path.join(self.UI_DIR, "log_dialog.ui")
            self.builder = gtk.Builder()
            self.builder.set_translation_domain('entertainer')
            self.builder.add_from_file(uifile)
        except RuntimeError:
            self.logger.critical("Couldn't open ui file: " + uifile)
            sys.exit(1)
        callback_dic = {
            "on_close_log_button_clicked" : self.on_close_log_button_clicked,
            "on_log_refresh_button_clicked" : self.update_log_rows,
            "on_checkbutton_debug_toggled" : self.filter_messages,
            "on_checkbutton_critical_toggled" : self.filter_messages,
            "on_checkbutton_error_toggled" : self.filter_messages,
            "on_checkbutton_warning_toggled" : self.filter_messages,
            "on_checkbutton_info_toggled" : self.filter_messages }

        self.builder.connect_signals(callback_dic)

        # Create log treeview
        treeview = self.builder.get_object("treeview_log")
        cell_renderer1 = gtk.CellRendererText()
        cell_renderer2 = gtk.CellRendererText()
        cell_renderer3 = gtk.CellRendererText()
        cell_renderer4 = gtk.CellRendererText()

        column1 = gtk.TreeViewColumn("Date")
        column1.pack_start(cell_renderer1, True)
        column1.set_attributes(cell_renderer1, text = 0)

        column2 = gtk.TreeViewColumn("Time")
        column2.pack_start(cell_renderer2, True)
        column2.set_attributes(cell_renderer2, text = 1)

        column3 = gtk.TreeViewColumn("Type")
        column3.pack_start(cell_renderer3, True)
        column3.set_attributes(cell_renderer3, text = 2)

        column4 = gtk.TreeViewColumn("Message")
        column4.pack_end(cell_renderer4, True)
        column4.set_attributes(cell_renderer4, text = 3)

        treeview.append_column(column1)
        treeview.append_column(column2)
        treeview.append_column(column3)
        treeview.append_column(column4)
        treeview.set_headers_visible(True)

        # Set model to view and read data from logfile
        self.log_store = gtk.ListStore(str, str, str, str)
        treeview.set_model(self.log_store)
        self.update_log_rows()

        # Show Log viewer dialog
        self.dialog = self.builder.get_object("LogDialog")
        self.dialog.resize(750, 500)
        self.dialog.connect("destroy", self.on_close_log_button_clicked)
        self.dialog.show()

    def update_log_rows(self, widget=None):
        """Read logfile and udpate treeview"""
        self.log_rows[:] = []

        try:
            for line in open(self.logfile_entertainer, 'r'):
                try:
                    line_table = line.split()
                    message = ' '.join(line_table[3:])
                    row = line_table[:3] + [message]
                    parsed_row = parse_row(row)
                    self.log_rows.append(parsed_row)
                except IndexError:
                    print "Cannot parse log line: ", line
        except IOError:
            print "Cannot find logfile: ", self.logfile_entertainer

        # Reverse so that the latest message is at top
        self.log_rows.reverse()
        # Filter unwated message types
        self.filter_messages()

    def filter_messages(self, widget = None):
        """Checks which message types should be displayed on treeview"""
        if self.log_store:
            self.log_store.clear()

        debug = self.builder.get_object("checkbutton_debug").get_active()
        critical = self.builder.get_object("checkbutton_critical").get_active()
        error = self.builder.get_object("checkbutton_error").get_active()
        warning = self.builder.get_object("checkbutton_warning").get_active()
        info = self.builder.get_object("checkbutton_info").get_active()

        for element in self.log_rows:
            if element[2] == "DEBUG" and debug:
                self.log_store.append(element)
            elif element[2] == "CRITICAL" and critical:
                self.log_store.append(element)
            elif element[2] == "ERROR" and error:
                self.log_store.append(element)
            elif element[2] == "WARNING" and warning:
                self.log_store.append(element)
            elif element[2] == "INFO" and info:
                self.log_store.append(element)

    # Signal handlers
    def on_close_log_button_clicked(self, widget):
        """
        If running as a stand alone process, quit.
        Otherwise only destroy dialog.
        """
        self.dialog.hide()
        self.dialog.destroy()
        if(self.__STAND_ALONE):
            gtk.main_quit()


def parse_row(row):
    """
    This parses the input list into a list suitable for the logviewer
    @author Joshua Scotton
    @param row The input list [Date, Time, Class, Type + Description]
    """
    if row[3][:5] == "DEBUG":
        return [row[0], row[1], "DEBUG",
            row[2] + ": " + row[3][5:]]
    elif row[3][:8] == "CRITICAL":
        return [row[0], row[1], "CRITICAL",
            row[2] + ": " + row[3][8:]]
    elif row[3][:5] == "ERROR":
        return [row[0], row[1], "ERROR",
            row[2] + ": " + row[3][5:]]
    elif row[3][:7] == "WARNING":
        return [row[0], row[1], "WARNING",
            row[2] + ": " + row[3][7:]]
    elif row[3][:4] == "INFO":
        return [row[0], row[1], "INFO",
            row[2] + ": " + row[3][4:]]

