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

from cpucompare.models.abstract import ModelAbstract
from cpucompare.models.info_cpumodel import InfoCPUModel


class CPUModels(ModelAbstract):
    COL_MODEL = 1
    COL_QUANTITY = 2
    COL_QUANTITY_CPU = 3
    COL_BRAND_KEY = 4
    COL_SERIES_KEY = 5
    COL_SCORE = 6
    COL_SCORE_RELATIVE = 7

    def add_data(self, item):
        """Add a new row to the model if it doesn't exist"""
        super(self.__class__, self).add_data(item)
        if f'{item.name}_{item.quantity}' not in self.rows:
            new_row = self.model.append((
                item.name,
                item.name,
                item.quantity,
                f'{item.quantity} CPU',
                item.brand,
                item.series,
                item.score,
                0.0,
            ))
            self.rows[f'{item.name}_{item.quantity}'] = new_row
            return new_row

    def get_model(self, treeiter):
        """Get the model from a TreeIter"""
        return self.model[treeiter][self.COL_MODEL]

    def get_score(self, treeiter):
        """Get the score from a TreeIter"""
        return self.model[treeiter][self.COL_SCORE]

    def get_brand(self, treeiter):
        """Get the brand name from a TreeIter"""
        return self.model[treeiter][self.COL_BRAND_KEY]

    def get_series(self, treeiter):
        """Get the series name from a TreeIter"""
        return self.model[treeiter][self.COL_SERIES_KEY]

    def get_quantity(self, treeiter):
        """Get the quantity from a TreeIter"""
        return self.model[treeiter][self.COL_QUANTITY]

    def get_info_cpumodel(self, name, quantity):
        treeiter = self.get_iter(f'{name}_{quantity}')
        result = InfoCPUModel(name,
                              self.get_score(treeiter),
                              quantity,
                              self.get_brand(treeiter),
                              self.get_series(treeiter))
        return result
