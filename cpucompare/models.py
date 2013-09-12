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

class CPUCompareModel(object):
  COL_VALUE = 0
  COL_KEY = 1
  def __init__(self, model):
    self.model = model

  def get_value(self, treeiter):
    return self.model[treeiter][self.__class__.COL_VALUE]

  def get_key(self, treeiter):
    return self.model[treeiter][self.__class__.COL_KEY]

  def clear(self):
    return self.model.clear()

  def append(self, *args):
    return self.model.append(*args)

  def count(self):
    return len(self.model)

class CPUCompareModelBrands(CPUCompareModel):
  def __init__(self, model):
    super(self.__class__, self).__init__(model)

class CPUCompareModelSeries(CPUCompareModel):
  def __init__(self, model):
    super(self.__class__, self).__init__(model)

class CPUCompareModelModels(CPUCompareModel):
  COL_SCORE = 2
  COL_QUANTITY = 3
  COL_BRANDKEY = 4
  COL_SERIESKEY = 5
  def __init__(self, model):
    super(self.__class__, self).__init__(model)

  def get_score(self, treeiter):
    return self.model[treeiter][self.__class__.COL_SCORE]

  def get_quantity(self, treeiter):
    return self.model[treeiter][self.__class__.COL_QUANTITY]

  def get_brand(self, treeiter):
    return self.model[treeiter][self.__class__.COL_BRANDKEY]

  def get_series(self, treeiter):
    return self.model[treeiter][self.__class__.COL_SERIESKEY]
