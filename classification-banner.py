#!/usr/bin/python
# Classification Banner
# Author: Frank Caviggia (fcaviggia@gmail.com)
# Copyright: Frank Caviggia, 2013
# Version: 1.2
# License: GPLv2

import sys
import os
import optparse

if not 'DISPLAY' in os.environ:
    print("Error: DISPLAY environment varible not set.")
    sys.exit(1)
import gtk

# Create a set of predefined profiles for known classification levels
class Profiles:
    """A collection of settings for pre-defined classification levels.

    Each profile is a dictionary containing the following keys:
        message -- The classification level to display
        fgcolor -- Foreground color of the text to display
        bgcolor -- Background color of the banner the text is against
        face    -- Font face to use for the displayed text
        size    -- Size of font to use for text
        weight  -- Bold or normal
    """

    U = { "face":"liberation-sans", "size":"small", "weight":"bold",
        "message":"UNCLASSIFIED", "fgcolor":"#000000", "bgcolor":"#00CC00"}
    C = { "face":"liberation-sans", "size":"small", "weight":"bold",
        "message":"CONFIDENTIAL", "fgcolor":"#000000", "bgcolor":"#33FFFF"}
    S = { "face":"liberation-sans", "size":"small", "weight":"bold",
        "message":"SECRET", "fgcolor":"#FFFFFF", "bgcolor":"#FF0000"}
    TS = { "face":"liberation-sans", "size":"small", "weight":"bold",
        "message":"TOP SECRET", "fgcolor":"#FFFFFF", "bgcolor":"#FF9900"}
    TS_SCI = { "face":"liberation-sans", "size":"small", "weight":"bold",
        "message":"TOP SECRET//SCI", "fgcolor":"#000000", "bgcolor":"#FFFF00"}

all_profiles = {
    'U':Profiles.U, 'UNCLASSIFIED':Profiles.U,
    'C':Profiles.C, 'CONFIDENTIAL':Profiles.C,
    'S':Profiles.S, 'SECRET':Profiles.S,
    'TS':Profiles.TS, 'TOP_SECRET':Profiles.TS,
    'TS_SCI':Profiles.TS_SCI, 'TOP_SECRET_SCI':Profiles.TS_SCI}


# Classifion Banner Class
class Classification_Banner:
    """Class to create and refresh the actual banner."""

    def __init__(self, message, fgcolor, bgcolor, face, size, weight):
        """Set up and display the main window

        Keyword arguments:
            message -- The classification level to display
            fgcolor -- Foreground color of the text to display
            bgcolor -- Background color of the banner the text is against
            face    -- Font face to use for the displayed text
            size    -- Size of font to use for text
            weight  -- Bold or normal
        """

        # Create Main Window
        self.window = gtk.Window()
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("delete_event", self.refresh)
        self.window.connect("destroy", self.refresh)
        self.window.connect("hide", self.restore)
        self.window.connect("window-state-event", self.restore)
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(bgcolor))
        self.window.set_property('skip-taskbar-hint', True)
        self.window.set_property('skip-pager-hint', True)
        self.window.set_property('destroy-with-parent', True)
        self.window.stick()
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_app_paintable(True)
        self.display = gtk.gdk.display_get_default()
        self.screen = self.display.get_default_screen()
        self.hres = self.screen.get_width()
        self.vres = self.screen.get_height()
        self.window.set_default_size(self.hres, 5)

        # Create Main Vertical Box to Populate
        self.vbox = gtk.VBox()

        self.label = gtk.Label(
            "<span font_family='%s' weight='%s' foreground='%s' size='%s'>%s</span>" %
            (face, weight, fgcolor, size, message))
        self.label.set_use_markup(True)
        self.label.set_justify(gtk.JUSTIFY_CENTER)
        self.vbox.pack_start(self.label, True, True, 0)

        self.window.add(self.vbox)
        self.window.show_all()
        self.width, self.height = self.window.get_size()

    def refresh(self, widget, data=None):
        run = Display_Banner()
        return True

    def restore(self, widget, data=None):
        self.window.present()
        return True

class Display_Banner:
    """Display Classification Banner Message"""

    def __init__(self):

        # Read configuration from command line options
        parser = optparse.OptionParser()
        parser.add_option("-p", "--profile",
            choices=all_profiles.keys(),
            help="Predefined profile. Valid values are U, C, S, TS, and TS_SCI. Note: additional options override profile settings")
        parser.add_option("-m", "--message", help="Classification message")
        parser.add_option("-f", "--fgcolor", help="Foreground (text) color")
        parser.add_option("-b", "--bgcolor", help="Background color")
        parser.add_option("--face", help="Font face")
        parser.add_option("--size", help="Font size")
        parser.add_option("--weight", help="Font weight")
        parser.add_option("--hide-top", default=True,
            dest="show_top", action="store_false",
            help="Disable the top banner")
        parser.add_option("--hide-bottom", default=True,
            dest="show_bottom", action="store_false",
            help="Disable the bottom banner")

        options, args = parser.parse_args()

        # Load the default configuration
        try:
            config = {}
            execfile("/etc/classification-banner", config)
        except:
            config = {}
            pass

        # Initialize based on a default profile
        default_profile = 'U'
        if 'profile' in config:
            default_profile = config['profile']
        if options.profile is not None:
            default_profile = options.profile
        cur_profile = all_profiles[default_profile]

        # Override profile settings using the global configuration file
        for k, v in config.items():
            if v is not None and k not in ['profile','show_top','show_bottom']:
                cur_profile[k] = v

        # Override profile settings using additional command line parameters
        for k, v in options.__dict__.items():
            if v is not None and k not in ['profile','show_top','show_bottom']:
                cur_profile[k] = v

        # Do what we came here to do
        if config.get('show_top', options.show_top):
            self.top = Classification_Banner(**cur_profile)
            self.top.window.move(0, 0)
        if config.get('show_bottom', options.show_bottom):
            self.bottom = Classification_Banner(**cur_profile)
            self.bottom.window.move(0, self.bottom.vres)

# Main Program Loop
if __name__ == "__main__":
    run = Display_Banner()
    gtk.main()
