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

from cpucompare.localize import _
from cpucompare.models.abstract import ModelAbstract


class CPUSelections(ModelAbstract):
    COL_INDEX = 1
    COL_MODEL = 2
    COL_QUANTITY = 3
    COL_QUANTITY_CPU = 4
    COL_BRAND_KEY = 5
    COL_SERIES_KEY = 6
    COL_SCORE = 7
    COL_SCORE_RELATIVE = 8

    def __init__(self, model, max_score):
        super(self.__class__, self).__init__(model)
        self.max_score = max_score

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        # Determine the new Index adding 1 to the last Index
        if len(self) == 0:
            new_index = 1
        else:
            new_index = int(self.get_key(len(self) - 1)) + 1
        if str(new_index) not in self.rows:
            new_row = self.model.append((
                '%05d' % new_index,
                new_index,
                item.name,
                item.quantity,
                '%d CPU' % item.quantity,
                item.brand if item.brand else _('Unknown brand'),
                item.series if item.series else _('Unknown series'),
                item.score,
                item.score * 100 / self.max_score,
            ))
            self.rows['%05d' % new_index] = new_row
            return new_row
