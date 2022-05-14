##
#     Project: CPUCompare
# Description: A GTK+ application to make comparisons between CPU models
#      Author: Fabio Castelli <muflone@muflone.com>
#   Copyright: 2013-2022 Fabio Castelli
#     License: GPL-2+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from cpucompare.gtkbuilder_loader import GtkBuilderLoader
from cpucompare.constants import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, APP_URL, APP_COPYRIGHT,
    APP_AUTHOR, APP_AUTHOR_EMAIL, DATABASE_VERSION,
    FILE_CONTRIBUTORS, FILE_LICENSE, FILE_TRANSLATORS, FILE_RESOURCES,
    FILE_ICON)
from cpucompare.functions import readlines
from cpucompare.localize import _


class UIAbout(object):
    def __init__(self, parent):
        """Prepare the about dialog"""
        # Retrieve the translators list
        translators = []
        for line in readlines(FILE_TRANSLATORS, False):
            if ':' in line:
                line = line.split(':', 1)[1]
            line = line.replace('(at)', '@').strip()
            if line not in translators:
                translators.append(line)
        # Load the user interface
        self.ui = GtkBuilderLoader('about.ui')
        # Set various properties
        self.ui.dialog_about.set_program_name(APP_NAME)
        self.ui.dialog_about.set_version('%s\n%s' % (
            _('Version %s') % APP_VERSION,
            _('Database version: %s') % DATABASE_VERSION))
        self.ui.dialog_about.set_comments(_(APP_DESCRIPTION))
        self.ui.dialog_about.set_website(APP_URL)
        self.ui.dialog_about.set_copyright(APP_COPYRIGHT)
        # Prepare lists for authors and contributors
        authors = ['%s <%s>' % (APP_AUTHOR, APP_AUTHOR_EMAIL)]
        contributors = []
        for line in readlines(FILE_CONTRIBUTORS, False):
            contributors.append(line)
        if len(contributors) > 0:
            contributors.insert(0, _('Contributors:'))
            authors.extend(contributors)
        self.ui.dialog_about.set_authors(authors)
        self.ui.dialog_about.set_license(
            '\n'.join(readlines(FILE_LICENSE, True)))
        self.ui.dialog_about.set_translator_credits('\n'.join(translators))
        # Retrieve the external resources links
        # only for GTK+ 3.6.0 and higher
        if not Gtk.check_version(3, 6, 0):
            for line in readlines(FILE_RESOURCES, False):
                resource_type, resource_url = line.split(':', 1)
                self.ui.dialog_about.add_credit_section(
                    resource_type, (resource_url,))
        icon_logo = Pixbuf.new_from_file(FILE_ICON)
        self.ui.dialog_about.set_logo(icon_logo)
        self.ui.dialog_about.set_transient_for(parent)

    def show(self):
        """Show the About dialog"""
        self.ui.dialog_about.run()
        self.ui.dialog_about.hide()

    def destroy(self):
        """Destroy the About dialog"""
        self.ui.dialog_about.destroy()
        self.ui.dialog_about = None
