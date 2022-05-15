##
#     Project: CPUCompare
# Description: A GTK+ application to make comparisons between CPU models
#      Author: Fabio Castelli <muflone@muflone.com>
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

from gi.repository.GdkPixbuf import Pixbuf

from cpucompare.constants import (APP_NAME,
                                  APP_VERSION,
                                  APP_URL,
                                  APP_COPYRIGHT,
                                  APP_AUTHOR,
                                  APP_AUTHOR_EMAIL,
                                  DATABASE_VERSION,
                                  FILE_LICENSE,
                                  FILE_TRANSLATORS,
                                  FILE_RESOURCES,
                                  FILE_ICON)
from cpucompare.functions import readlines
from cpucompare.localize import _
from cpucompare.ui.base import UIBase


class UIAbout(UIBase):
    def __init__(self, parent):
        """Prepare the about dialog"""
        super().__init__(filename='about.ui')
        # Retrieve the translators list
        translators = []
        for line in readlines(FILE_TRANSLATORS, False):
            if ':' in line:
                line = line.split(':', 1)[1]
            line = line.replace('(at)', '@').strip()
            if line not in translators:
                translators.append(line)
        # Set various properties
        self.ui.dialog_about.set_program_name(APP_NAME)
        self.ui.dialog_about.set_version(
            _('Version {VERSION}\nDatabase version {DATABASE_VERSION}').format(
                VERSION=APP_VERSION,
                DATABASE_VERSION=DATABASE_VERSION))
        self.ui.dialog_about.set_comments(
            _('Make comparisons between CPU models.'))
        self.ui.dialog_about.set_website(APP_URL)
        self.ui.dialog_about.set_copyright(APP_COPYRIGHT)
        # Prepare lists for authors
        authors = ['%s <%s>' % (APP_AUTHOR, APP_AUTHOR_EMAIL)]
        self.ui.dialog_about.set_authors(authors)
        self.ui.dialog_about.set_license(
            '\n'.join(readlines(FILE_LICENSE, True)))
        self.ui.dialog_about.set_translator_credits('\n'.join(translators))
        # Retrieve the external resources links
        for line in readlines(FILE_RESOURCES, False):
            resource_type, resource_url = line.split(':', 1)
            self.ui.dialog_about.add_credit_section(
                resource_type, (resource_url,))
        icon_logo = Pixbuf.new_from_file(str(FILE_ICON))
        self.ui.dialog_about.set_logo(icon_logo)
        self.ui.dialog_about.set_transient_for(parent)
        # Connect signals from the UI file to the functions with the same name
        self.ui.connect_signals(self)

    def show(self):
        """Show the About dialog"""
        self.ui.dialog_about.run()
        self.ui.dialog_about.hide()

    def destroy(self):
        """Destroy the About dialog"""
        self.ui.dialog_about.destroy()
        self.ui.dialog_about = None
