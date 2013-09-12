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

import sys
import os.path

APP_NAME='CPUCompare'
APP_VERSION='0.4'
APP_DESCRIPTION='A GTK+ application to make comparisons between CPU models.'
APP_ID='cpucompare.muflone.com'
APP_URL='https://github.com/muflone/cpucompare'
APP_AUTHOR='Fabio Castelli'
APP_AUTHOR_EMAIL='webreg@vbsimple.net'
APP_COPYRIGHT='Copyright 2013 %s' % APP_AUTHOR

# If there's a file data/cpucompare.db then the shared data are searched in
# relative paths, else the standard paths are used
if os.path.isfile(os.path.join('data', 'cpucompare.db')):
  DIR_PREFIX='.'
else:
  DIR_PREFIX=os.path.join(sys.prefix, 'share', 'cpucompare')

DIR_DATA=os.path.join(DIR_PREFIX, 'data')
DIR_UI=os.path.join(DIR_PREFIX, 'ui')
DATABASE_VERSION=20130806
