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

import os.path
from gi.repository import GObject

from cpucompare.sqlite3_connection import SQLite3Connection
from cpucompare.daemon_thread import DaemonThread
from cpucompare.constants import DIR_DATA

from cpucompare.models.info_cpubrand import InfoCPUBrand
from cpucompare.models.info_cpuseries import InfoCPUSeries
from cpucompare.models.info_cpumodel import InfoCPUModel

database = None


class ModelsDB(object):
    def __init__(self):
        self.loader = None
        self.cb_add_row = None
        self.database = SQLite3Connection()
        self.database.open(os.path.join(DIR_DATA, 'cpucompare.db'))

    def close(self):
        """Close the database connection"""
        if self.loader.isAlive():
            # If the loader thread is alive, first cancel it
            self.loader.cancel()
            self.loader.join()
        self.database.close()

    def load(self, cb_add_row):
        """Load the data from the database"""
        self.cb_add_row = cb_add_row
        self.loader = DaemonThread(self.__load_all_models)
        self.loader.start()

    def __load_all_models(self):
        """Load all models"""
        sSQL = 'SELECT cpu_name, score1, quantity, brand, model1 FROM cpu ' \
               'ORDER BY cpu_name'
        for row in self.database.execute(sSQL):
            # Cancel the running thread
            if self.loader.cancelled:
                break
            # Add the row in a thread safe way
            model = InfoCPUModel(row['cpu_name'],
                                 row['score1'],
                                 row['quantity'],
                                 row['brand'],
                                 row['model1'])
            GObject.idle_add(self.cb_add_row, model)
        return False

    def get_models_count(self):
        """Return the number of models in the database"""
        sSQL = 'SELECT count(*) AS totals FROM cpu'
        return self.database.execute(sSQL).fetchall()[0]['totals']

    def get_max_score(self):
        """Return the max score in the database"""
        sSQL = 'SELECT max(score1) AS score FROM cpu'
        return self.database.execute(sSQL).fetchall()[0]['score']

    def get_brands(self, cpu_quantity):
        """Return a list of InfoCPUBrand"""
        sSQL = 'SELECT DISTINCT brand ' \
               'FROM cpu ' \
               'WHERE quantity %s 1 ' \
               'ORDER BY brand' % self._get_quantity_sign(cpu_quantity)
        result = []
        for row in self.database.execute(sSQL):
            result.append(InfoCPUBrand(row['brand'],
                                       row['brand']))
        return result

    def get_series(self, cpu_quantity, brand_name):
        """Return a list of InfoCPUSeries"""
        sSQL = 'SELECT DISTINCT model1 ' \
               'FROM cpu ' \
               'WHERE quantity %s 1 ' \
               'AND brand=? ' \
               'ORDER BY model1' % self._get_quantity_sign(cpu_quantity)
        result = []
        for row in self.database.execute(sSQL, brand_name):
            result.append(InfoCPUSeries(row['model1'],
                                        row['model1']))
        return result

    def get_models(self, cpu_quantity, brand_name, series_name):
        """Return a list of InfoCPUModel"""
        sSQL = 'SELECT cpu_name, model1, quantity, score1 ' \
               'FROM cpu ' \
               'WHERE quantity %s 1 ' \
               'AND brand=? ' \
               'AND model1=? ' \
               'ORDER BY cpu_name, ' \
               '         quantity' % self._get_quantity_sign(cpu_quantity)
        result = []
        for row in self.database.execute(sSQL, brand_name, series_name):
            result.append(InfoCPUModel(row['cpu_name'],
                                       row['score1'],
                                       row['quantity'],
                                       brand_name,
                                       series_name))
        return result

    def _get_quantity_sign(self, cpu_quantity):
        """
        Return the sign to check the CPU quantity:
          =  for 1 CPU
          >  for 2+ CPU
          >= for 1+ CPU
        """
        return {'1': '=', '2': '>'}.get(str(cpu_quantity), '>=')
