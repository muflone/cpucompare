##
#     Project: CPUCompare
# Description: A GTK+ application to make comparisons between CPU models
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2013-2022 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

import logging

from gi.repository import Gtk

from cpucompare.localize import text
from cpucompare.ui.base import UIBase


class UIShortcuts(UIBase):
    def __init__(self, parent, settings, options):
        """Prepare the dialog"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='shortcuts.ui')
        # Initialize members
        self.settings = settings
        self.options = options
        # Load the user interface
        self.ui.shortcuts.set_transient_for(parent)
        # Initialize groups
        for widget in self.ui.get_objects_by_type(Gtk.ShortcutsGroup):
            widget.props.title = text(widget.props.title)
        # Initialize shortcuts
        for widget in self.ui.get_objects_by_type(Gtk.ShortcutsShortcut):
            widget.props.title = text(widget.props.title)

    def show(self):
        """Show the dialog"""
        logging.debug(f'{self.__class__.__name__} show')
        self.ui.shortcuts.show()

    def destroy(self):
        """Destroy the dialog"""
        logging.debug(f'{self.__class__.__name__} destroy')
        self.ui.shortcuts.destroy()
        self.ui.shortcuts = None
