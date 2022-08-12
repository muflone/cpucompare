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

import sqlite3


class SQLite3Connection(object):
    def __init__(self, database=None):
        """Initialize a SQLite3 database"""
        self.connection = None
        # Automatically open the database if its file path was provided
        if database:
            self.open(database)

    def open(self, database):
        """Open the database connection"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def close(self):
        """Close the database connection"""
        self.connection.close()
        self.connection = None

    def execute(self, sql, *arguments):
        """Execute an instruction and return its data"""
        cursor = self.connection.cursor()
        if len(arguments) == 1 and arguments[0] is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, arguments)
        return cursor
