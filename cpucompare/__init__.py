##
#     Project: CPUCompare
# Description: A GTK+ application to make comparisons between CPU models
#      Author: Fabio Castelli <muflone@vbsimple.net>
#   Copyright: 2013-2017 Fabio Castelli
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

import gettext
import locale

import cpucompare.requires

from cpucompare.localize import store_message, text, _
from cpucompare.constants import DOMAIN_NAME, DIR_LOCALE

def strip_colon(message):
    """Remove the colons from the message"""
    return message.replace(':', '')


def strip_underline(message):
    """Remove the underlines from the message"""
    return message.replace('_', '')


# Load domain for translation
for module in (gettext, locale):
    module.bindtextdomain(DOMAIN_NAME, DIR_LOCALE)
    module.textdomain(DOMAIN_NAME)

# Import some translated messages from GTK+ domain
for message in ('_Remove', '_Clear List', 'Properties'):
    text(message=message, gtk30=True)

# Import some variations
store_message('Type:', '%s:' % text(message='Type', gtk30=True))
for message in ('_Brand:', 'S_eries:', 'M_odel:', 'Score:'):
    new_message = strip_colon(strip_underline(message))
    store_message(new_message,
                  strip_colon(strip_underline(text(message=message,
                                                   gtk30=False))))

# With domain context
for message in ('_Quit', '_Add'):
    text(message=message, gtk30=True, context='Stock label')
store_message('Quit', text(message='_Quit', gtk30=True).replace('_', ''))
