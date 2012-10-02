# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''UserInterface - Main window of the Entertainer client'''

# Clutter uses _1 to represent the 1 key and pylint complains about it
# pylint: disable-msg=W0212

from collections import defaultdict
import os

import cluttergtk
import clutter
import gobject
import gtk

from entertainerlib.client.media_player import MediaPlayer
from entertainerlib.configuration import Configuration
from entertainerlib.gui.widgets.volume_indicator import VolumeIndicator
from entertainerlib.gui.screen_history import ScreenHistory
from entertainerlib.gui.screens.factory import ScreenFactory
from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.transitions.factory import TransitionFactory
from entertainerlib.gui.transitions.transition import Transition
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.menu_overlay import MenuOverlay
from entertainerlib.logger import Logger


class UserInterface:
    '''A main GUI window of the Entertainer client.'''

    def __init__(self, image_library, music_library, video_library,
        quit_client_callback):
        self.quit_client_callback = quit_client_callback
        self.config = Configuration()

        # Store the dimensions in case users want to return to window mode
        self.old_width = self.config.stage_width
        self.old_height = self.config.stage_height

        self.logger = Logger().getLogger('client.gui.UserInterface')

        self.window = gtk.Window()
        self.window.connect('destroy', self.destroy_callback)
        self.window.set_title('Entertainer')

        # Set the window icon
        icon_theme = gtk.icon_theme_get_default()
        try:
            icon = icon_theme.load_icon('entertainer', 48, 0)
            self.window.set_icon(icon)
        except gobject.GError:
            # Must not be installed from a package, get icon from the branch
            file_dir = os.path.dirname(__file__)
            icon_path = os.path.join(file_dir, '..', '..', 'icons',
                'hicolor', '48x48', 'apps', 'entertainer.png')
            icon = gtk.gdk.pixbuf_new_from_file(icon_path)
            self.window.set_icon(icon)

        # cluttergtk.Embed contains the stage that is the canvas for the GUI
        embed = cluttergtk.Embed()
        # Enforce a minimum size to prevent weird widget bugs
        embed.set_size_request(
            self.config.stage_width, self.config.stage_height)
        self.window.add(embed)

        # The embed widget must be realized before you can get the stage.
        embed.realize()
        self.stage = embed.get_stage()

        self._hide_cursor_timeout_key = None

        self.stage.connect('key-press-event', self.handle_keyboard_event)
        self.stage.connect('motion-event', self._handle_motion_event)
        self.stage.set_color(self.config.theme.get_color("background"))
        self.stage.set_size(self.config.stage_width, self.config.stage_height)
        self.stage.set_title("Entertainer")

        if self.config.start_in_fullscreen:
            self._fullscreen()
            self.is_fullscreen = True
        else:
            self.is_fullscreen = False

        # Initialize Screen history (allows user to navigate "back")
        self.history = ScreenHistory(self._remove_from_stage)

        self.player = MediaPlayer(self.stage,
            self.config.stage_width, self.config.stage_height)
        self.player.connect('volume-changed', self._on_volume_changed)

        # Initialize menu overlay texture
        self.is_overlay = False
        self.menu_overlay = MenuOverlay(self.config.theme)
        self.menu_overlay.set_opacity(0)
        self.menu_overlay.set_size(
            self.config.stage_width, self.config.stage_height)
        self.stage.add(self.menu_overlay)

        self.volume_indicator = VolumeIndicator()
        self.stage.add(self.volume_indicator)
        self.volume_indicator.connect('hiding',
            self._on_volume_indicator_hiding)
        self.fade_screen_timeline = clutter.Timeline(200)
        alpha = clutter.Alpha(self.fade_screen_timeline,
            clutter.EASE_IN_OUT_SINE)
        self.fade_screen_behaviour = clutter.BehaviourOpacity(255, 0, alpha)

        # Transition object. Handles effects between screen changes.
        transition_factory = TransitionFactory(self._remove_from_stage)
        self.transition = transition_factory.generate_transition()

        # Screen factory to create new screens
        self.screen_factory = ScreenFactory(
            image_library, music_library, video_library, self.player,
            self.move_to_new_screen, self.move_to_previous_screen)

        def default_key_to_user_event():
            '''Return the default user event provided by an unmapped keyboard
            event.'''
            return UserEvent.DEFAULT_EVENT

        # Dictionary for keyboard event handling
        self.key_to_user_event = defaultdict(default_key_to_user_event, {
            clutter.keysyms.Return : UserEvent.NAVIGATE_SELECT,
            clutter.keysyms.Up : UserEvent.NAVIGATE_UP,
            clutter.keysyms.Down : UserEvent.NAVIGATE_DOWN,
            clutter.keysyms.Left : UserEvent.NAVIGATE_LEFT,
            clutter.keysyms.Right : UserEvent.NAVIGATE_RIGHT,
            clutter.keysyms.BackSpace : UserEvent.NAVIGATE_BACK,
            clutter.keysyms.h : UserEvent.NAVIGATE_HOME,
            clutter.keysyms.w : UserEvent.NAVIGATE_FIRST_PAGE,
            clutter.keysyms.e : UserEvent.NAVIGATE_PREVIOUS_PAGE,
            clutter.keysyms.r : UserEvent.NAVIGATE_NEXT_PAGE,
            clutter.keysyms.t : UserEvent.NAVIGATE_LAST_PAGE,
            clutter.keysyms.f : UserEvent.TOGGLE_FULLSCREEN,
            clutter.keysyms.p : UserEvent.PLAYER_PLAY_PAUSE,
            clutter.keysyms.s : UserEvent.PLAYER_STOP,
            clutter.keysyms._1 : UserEvent.USE_ASPECT_RATIO_1,
            clutter.keysyms._2 : UserEvent.USE_ASPECT_RATIO_2,
            clutter.keysyms._3 : UserEvent.USE_ASPECT_RATIO_3,
            clutter.keysyms._4 : UserEvent.USE_ASPECT_RATIO_4,
            clutter.keysyms.x : UserEvent.PLAYER_SKIP_BACKWARD,
            clutter.keysyms.c : UserEvent.PLAYER_SKIP_FORWARD,
            clutter.keysyms.z : UserEvent.PLAYER_PREVIOUS,
            clutter.keysyms.v : UserEvent.PLAYER_NEXT,
            clutter.keysyms.m : UserEvent.PLAYER_VOLUME_UP,
            clutter.keysyms.l : UserEvent.PLAYER_VOLUME_DOWN,
            clutter.keysyms.q : UserEvent.QUIT,
            clutter.keysyms.Escape : UserEvent.QUIT
        })

        self.event_handlers = {
            UserEvent.DEFAULT_EVENT : self._handle_default,
            UserEvent.NAVIGATE_SELECT : self._handle_default,
            UserEvent.NAVIGATE_UP : self._handle_default,
            UserEvent.NAVIGATE_DOWN : self._handle_default,
            UserEvent.NAVIGATE_LEFT : self._handle_default,
            UserEvent.NAVIGATE_RIGHT : self._handle_default,
            UserEvent.NAVIGATE_BACK : self._handle_navigate_back,
            UserEvent.NAVIGATE_HOME : self._handle_navigate_home,
            UserEvent.NAVIGATE_FIRST_PAGE : self._handle_default,
            UserEvent.NAVIGATE_PREVIOUS_PAGE : self._handle_default,
            UserEvent.NAVIGATE_NEXT_PAGE : self._handle_default,
            UserEvent.NAVIGATE_LAST_PAGE : self._handle_default,
            UserEvent.TOGGLE_FULLSCREEN : self._handle_toggle_fullscreen,
            UserEvent.PLAYER_PLAY_PAUSE : self._handle_player_play_pause,
            UserEvent.PLAYER_STOP : self._handle_player_stop,
            UserEvent.USE_ASPECT_RATIO_1 : self._handle_aspect_ratio,
            UserEvent.USE_ASPECT_RATIO_2 : self._handle_aspect_ratio,
            UserEvent.USE_ASPECT_RATIO_3 : self._handle_aspect_ratio,
            UserEvent.USE_ASPECT_RATIO_4 : self._handle_aspect_ratio,
            UserEvent.PLAYER_SKIP_BACKWARD : self._handle_player_skip_backward,
            UserEvent.PLAYER_SKIP_FORWARD : self._handle_player_skip_forward,
            UserEvent.PLAYER_PREVIOUS : self._handle_player_previous,
            UserEvent.PLAYER_NEXT : self._handle_player_next,
            UserEvent.PLAYER_VOLUME_UP : self._handle_player_volume_up,
            UserEvent.PLAYER_VOLUME_DOWN : self._handle_player_volume_down,
            UserEvent.QUIT : self._handle_quit_client
        }

        self.logger.debug("Frontend GUI initialized succesfully")

    def _fullscreen(self):
        '''Set the window, stage, and config to fullscreen dimensions.'''
        self.window.fullscreen()
        self.stage.set_fullscreen(True)
        self.config.stage_width = int(gtk.gdk.screen_width())
        self.config.stage_height = int(gtk.gdk.screen_height())

    def destroy_callback(self, widget):
        '''Handle the GTK destroy signal and close gracefully.'''
        self.shutdown()

    def confirm_exit(self):
        '''Confirm that the user wants to shut down.'''
        if self.current.name == "Question":
            # Confirmation dialog is already displayed.
            return

        kwargs = {
            'question' : _('Are you sure you want to exit Entertainer?'),
            'answers' : (_('Yes'), _('No')),
            'callbacks' : (self.shutdown, None)
        }
        self.move_to_new_screen("question", kwargs)

    def start_up(self):
        '''Start the user interface and make it visible.'''
        self.show()
        self.stage.hide_cursor()
        self.current = self.create_screen("main")
        self.transition.forward_effect(None, self.current)
        self.enable_menu_overlay()

    def shutdown(self):
        '''Shut down the user interface.'''
        self.quit_client_callback()

    def _toggle_fullscreen(self):
        '''Set the User Interface to fullscreen mode or back to window mode.'''
        if self.is_fullscreen:
            self.stage.set_fullscreen(False)
            self.window.unfullscreen()
            self.config.stage_width = self.old_width
            self.config.stage_height = self.old_height
            self.is_fullscreen = False
        else:
            self._fullscreen()
            self.is_fullscreen = True

    def create_screen(self, screen_type, data=None):
        '''Delegate to the screen factory to generate a screen.'''
        screen = self.screen_factory.generate_screen(screen_type, data)
        self.stage.add(screen)
        return screen

    def move_to_new_screen(self, screen_type, kwargs=None,
        transition=Transition.FORWARD):
        '''Callback method for screens and tabs to ask for new screens'''
        screen = self.create_screen(screen_type, kwargs)
        self.change_screen(screen, transition)

    def move_to_previous_screen(self):
        '''Callback method to return to the previous screen in history.'''
        screen = self.history.get_screen()
        screen.update()
        self.change_screen(screen, Transition.BACKWARD)

    def show(self):
        '''Show the user interface.'''
        self.window.show_all()

    def hide(self):
        '''Hide the user interface.'''
        self.window.hide_all()

    def _remove_from_stage(self, group):
        '''Remove the listed group from the stage'''
        self.stage.remove(group)

    def enable_menu_overlay(self):
        """
        Enable menu overlay. Overlay should be enabled always when there is
        a video playing and menu showing at the same time. Overlay is not part
        of any specific screen. It is used for all screens when neccesary.
        """
        if not self.is_overlay:
            self.is_overlay = True
            self.menu_overlay.fade_in()
            self.player.is_reactive_allowed = False

    def disable_menu_overlay(self):
        """
        Disable menu overlay. Overlay should be disabled when current screen is
        a type of Screen.OSD.
        """
        if self.is_overlay:
            self.is_overlay = False
            self.menu_overlay.fade_out()
            self.player.is_reactive_allowed = True

    def change_screen(self, screen, direction):
        '''Transition the given screen in the direction provided.'''
        # Enable/Disable menu overlay
        if screen.kind == Screen.OSD:
            self.disable_menu_overlay()
        else:
            self.enable_menu_overlay()

        # Add current screen to screen history
        if direction == Transition.FORWARD:
            self.history.add_screen(self.current)

        # Change screen (Logical). Graphics is changed via animation
        from_screen = self.current
        self.current = screen

        # Animate screen change
        if direction == Transition.FORWARD:
            self.transition.forward_effect(from_screen, screen)
        elif direction == Transition.BACKWARD:
            self.transition.backward_effect(from_screen, screen)

    def _hide_cursor_timeout_callback(self):
        '''Hide the cursor'''
        self.stage.hide_cursor()
        return True

    def _handle_motion_event(self, stage, clutter_event):
        '''Show the cursor and start a timeout to hide it after 4 seconds.'''
        self.stage.show_cursor()
        if self._hide_cursor_timeout_key is not None:
            gobject.source_remove(self._hide_cursor_timeout_key)
        self._hide_cursor_timeout_key = gobject.timeout_add(4000,
            self._hide_cursor_timeout_callback)

    def handle_keyboard_event(self, stage, clutter_event, event_handler=None):
        '''Translate all received keyboard events to UserEvents.'''
        if event_handler is None:
            event_handler = self.handle_user_event

        user_event = self.key_to_user_event[clutter_event.keyval]
        event_handler(UserEvent(user_event))

    def handle_user_event(self, event):
        '''Delegate the user event to its proper handler method.'''
        kind = event.get_type()
        self.event_handlers[kind](event)

    def _handle_aspect_ratio(self, event):
        '''Handle UserEvent.USE_ASPECT_RATIO_*.'''
        kind = event.get_type()

        set_methods = {
            UserEvent.USE_ASPECT_RATIO_1 : self.player.set_native_ratio,
            UserEvent.USE_ASPECT_RATIO_2 : self.player.set_widescreen_ratio,
            UserEvent.USE_ASPECT_RATIO_3 : self.player.set_zoom_ratio,
            UserEvent.USE_ASPECT_RATIO_4 : self.player.set_intelligent_ratio
        }

        set_methods[kind]()
        self.current.handle_user_event(event)

    def _handle_default(self, event):
        '''Handle the most basic case where the event is passed to the current
        screen.'''
        self.current.handle_user_event(event)

    def _handle_navigate_back(self, event):
        '''Handle UserEvent.NAVIGATE_BACK.'''
        if not self.history.is_empty:
            self.move_to_previous_screen()

    def _handle_navigate_home(self, event):
        '''Handle UserEvent.NAVIGATE_HOME.'''
        self.move_to_new_screen('main')

    def _handle_player_next(self, event):
        '''Handle UserEvent.PLAYER_NEXT.'''
        self.player.next()

    def _handle_player_play_pause(self, event):
        '''Handle UserEvent.PLAYER_PLAY_PAUSE.'''
        if self.current.is_interested_in_play_action():
            self.current.execute_play_action()
        else:
            if self.player.is_playing:
                self.player.pause()
                self.current.handle_user_event(event)
            else:
                self.player.play()
                self.current.handle_user_event(event)

    def _handle_player_previous(self, event):
        '''Handle UserEvent.PLAYER_PREVIOUS.'''
        self.player.previous()

    def _handle_player_skip_backward(self, event):
        '''Handle UserEvent.PLAYER_SKIP_BACKWARD.'''
        self.player.skip_backward()
        self.current.handle_user_event(event)

    def _handle_player_skip_forward(self, event):
        '''Handle UserEvent.PLAYER_SKIP_FORWARD.'''
        self.player.skip_forward()
        self.current.handle_user_event(event)

    def _handle_player_stop(self, event):
        '''Handle UserEvent.PLAYER_STOP.'''
        if self.player.is_playing:
            self.player.stop()
            self.current.handle_user_event(event)

    def _handle_player_volume_up(self, event):
        '''Handle UserEvent.PLAYER_VOLUME_UP.'''
        self.player.volume_up()

    def _handle_player_volume_down(self, event):
        '''Handle UserEvent.PLAYER_VOLUME_DOWN.'''
        self.player.volume_down()

    def _handle_toggle_fullscreen(self, event):
        '''Handle UserEvent.TOGGLE_FULLSCREEN.'''
        self._toggle_fullscreen()

    def _handle_quit_client(self, event):
        '''Handle UserEvent.QUIT.'''
        self.confirm_exit()

    def _on_volume_changed(self, event):
        '''Show volume indicator and fade out the screen (if needed).'''
        if not self.volume_indicator.visible:
            if not self.fade_screen_behaviour.is_applied(self.current):
                self.fade_screen_behaviour.apply(self.current)
            self.fade_screen_behaviour.set_bounds(255, 50)
            self.fade_screen_timeline.start()

        self.volume_indicator.show_volume(self.player.volume)

    def _on_volume_indicator_hiding(self, event):
        '''Restore previous screen opacity.'''
        self.fade_screen_behaviour.set_bounds(50, 255)
        self.fade_screen_timeline.start()

