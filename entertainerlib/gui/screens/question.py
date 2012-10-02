# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Question - Screen displays a question label and specified buttons.'''

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.text_menu import TextMenu

class Question(Screen):
    '''Screen is displayed when the application needs to ask a close ended
    question to the user.'''

    def __init__(self, move_to_previous_screen_callback, question,
        answers, callbacks=None):
        Screen.__init__(self, 'Question')

        self.move_to_previous_screen_callback = move_to_previous_screen_callback
        self.answers = answers

        if callbacks is None:
            callbacks = []
        self.callbacks = callbacks

        screen_title = Label(0.13, "screentitle", 0, 0.87, _("Question"))
        self.add(screen_title)

        question_label = Label(0.04167, "text", 0.095, 0.13, str(question))
        self.add(question_label)

        self.menu = None
        self.display_answers()

    def display_answers(self):
        '''Display a menu with answers on the screen.'''
        self.menu = TextMenu(0.095, 0.5, 0.4393, 0.0781)
        self.menu.set_name("questionmenu")
        self.menu.connect('selected', self._handle_select)

        for answer in self.answers:
            self.menu.add_item(str(answer), None, str(answer))

        self.menu.active = True
        self.add(self.menu)

    def question_callback(self, selected_answer):
        '''Call the method associated with the selected answer.'''
        callback_loc = 0
        for answer in self.answers:
            if str(answer) == selected_answer:
                break
            callback_loc += 1

        if callback_loc < len(self.callbacks):
            callback = self.callbacks[callback_loc]
            if callback != None:
                callback()

    def go_back(self):
        '''Go back to previous screen'''
        self.move_to_previous_screen_callback()

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.menu.up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.menu.down()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        self.question_callback(self.menu.selected_userdata)
        self.go_back()

