##
#     Project: CPUCompare
# Description: A GTK+ application to make comparisons between CPU models
#      Author: Fabio Castelli <muflone@vbsimple.net>
#   Copyright: 2013 Fabio Castelli
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

import sqlite3

class SQLite3Connection(object):
  def __init__(self, sDatabase=None):
    self.connection = None
    # Automatically open the database if its file path was provided
    if sDatabase:
      self.open(sDatabase)

  def open(self, sDatabase):
    # Open the database connection
    self.connection = sqlite3.connect(sDatabase)

  def close(self):
    # Close the database connection
    self.connection.close()
    self.connection = None

  def select(self, sSQL, *arguments):
    # Execute an instruction and return its data
    cursor = self.connection.cursor()
    if len(arguments) == 1 and arguments[0] is None:
      cursor.execute(sSQL)
    else:
      cursor.execute(sSQL, arguments)
    return cursor
