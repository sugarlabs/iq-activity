# activity.py
# my standard link between sugar and my activity

import IQ
import sugargame.canvas
from sugar3.activity.activity import PREVIEW_SIZE
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity import activity
import pygame
from gi.repository import GLib
from gi.repository import Gtk
from gettext import gettext as _

import gi
gi.require_version('Gtk', '3.0')


class PeterActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.max_participants = 1

        # Create the game instance.
        self.game = IQ.IQ(self)

        # Note that set_canvas implicitly calls
        # read_file when resuming from the Journal.
        self._pygamecanvas = sugargame.canvas.PygameCanvas(
            self, main=self.game.run,
            modules=[pygame.display])

        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()
        self.build_toolbar()
        # Start the game running.
        # self._pygamecanvas.run_pygame(self.game.run)

    def build_toolbar(self):
        # Build the activity toolbar.
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()
        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()
        self.show_all()

    def read_file(self, file_path):
        try:
            f = open(file_path, 'r')
        except Exception:
            return  # ****
        self.game.load(f)
        f.close()

    def write_file(self, file_path):
        f = open(file_path, 'w')
        self.game.save(f)
        f.close()

    def get_preview(self):
        return self._pygamecanvas.get_preview()
