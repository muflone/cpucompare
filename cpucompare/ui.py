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

from gi.repository import Gtk
from gi.repository import Gio
from constants import *
import os.path

class CPUCompareUI(Gtk.Application):
  def __init__(self, database):
    Gtk.Application.__init__(self, application_id=APP_ID,
      flags=Gio.ApplicationFlags.FLAGS_NONE)
    self.loadUI(os.path.join(DIR_UI, 'cpucompare.glade'))
    self.database = database
    # Determine max score for relative score
    for row in self.database.select('SELECT MAX(score1) FROM cpu'):
      self.lMaxScore = row[0]

  def run(self):
    self.on_optCPUType_toggled(self.optCPUType1)
    self.winMain.show_all()
    Gtk.main()

  def loadUI(self, sFilename):
    builder = Gtk.Builder()
    builder.add_from_file(sFilename)
    # Obtain widget references
    self.winMain = builder.get_object("winMain")
    self.winMain.set_title(APP_NAME)
    self.optCPUType1 = builder.get_object("optCPUType1")
    self.optCPUTypeN = builder.get_object("optCPUTypeN")
    self.optCPUTypeAll = builder.get_object("optCPUTypeAll")
    for widget in self.optCPUTypeAll.get_group():
      if widget.get_active():
        self.oSelectedCPUType = widget
        break
    self.storeBrands = builder.get_object('storeBrands')
    self.storeSeries = builder.get_object('storeSeries')
    self.storeModels = builder.get_object('storeModels')
    self.storeCompares = builder.get_object('storeCompares')
    self.cboBrands = builder.get_object('cboBrands')
    self.cboSeries = builder.get_object('cboSeries')
    self.cboModels = builder.get_object('cboModels')
    self.lblScore2 = builder.get_object('lblScore2')
    self.tvwCompares = builder.get_object('tvwCompares')
    # Connect signals from the glade file to the functions with the same name
    builder.connect_signals(self)

  def on_winMain_delete_event(self, widget, event):
    # Disconnect from the database and close
    self.database.close()
    Gtk.main_quit()

  def on_optCPUType_toggled(self, widget):
    # Do nothing if the signal is fired for the disabled state
    if widget.get_active():
      # Save the previous brand
      if self.cboBrands.get_active() >= 0:
        sPreviousBrand = self.storeBrands[self.cboBrands.get_active()][1]
      else:
        sPreviousBrand = None
      # Determine which brands to extract
      sSQL = 'SELECT DISTINCT brand FROM cpu'
      if widget is self.optCPUType1:
        sSQL += ' WHERE quantity=1'
      elif widget is self.optCPUTypeN:
        sSQL += ' WHERE quantity>1'
      elif widget is self.optCPUTypeAll:
        pass
      else:
        assert(False)
      self.oSelectedCPUType = widget
      sSQL += ' ORDER BY brand'
      # Clear the model and load the brands
      self.storeBrands.clear()
      for row in self.database.select(sSQL):
        # Add each row in the ListStore
        oLastTreeIter = self.storeBrands.append(
          len(row[0]) == 0 and ('Unknown', '') or (row[0], row[0])
        )
        # Restore the previously selected brand
        if sPreviousBrand == row[0]:
          self.cboBrands.set_active_iter(oLastTreeIter)
      if self.cboBrands.get_active() < 0 and len(self.storeBrands) > 0:
        self.cboBrands.set_active(0)

  def on_cboBrands_changed(self, widget):
    # Load the series for the requested brand
    self.storeSeries.clear()
    iSelectedRowIndex = widget.get_active()
    if iSelectedRowIndex >= 0:
      brand = self.storeBrands[iSelectedRowIndex][0]
      sSQL = 'SELECT DISTINCT model1 FROM cpu WHERE brand=?'
      # Determine the cpu type to extract
      if self.oSelectedCPUType is self.optCPUType1:
        sSQL += ' AND quantity=1'
      elif self.oSelectedCPUType is self.optCPUTypeN:
        sSQL += ' AND quantity>1'
      sSQL += ' ORDER BY model1'
      for row in self.database.select(sSQL, brand):
        self.storeSeries.append((len(row[0]) > 0 and row[0] or 'Unknown',
          row[0]))
      # Automatically set the first item
      if len(self.storeSeries) > 0:
        self.cboSeries.set_active(0)

  def on_cboSeries_changed(self, widget):
    # Load the models for the requested series
    self.storeModels.clear()
    iSelectedRowIndex = self.cboSeries.get_active()
    if iSelectedRowIndex >= 0:
      series = self.storeSeries[iSelectedRowIndex][1]
      sSQL = 'SELECT cpu_name, score1, quantity FROM cpu WHERE model1=?'
      # Determine the cpu type to extract
      if self.oSelectedCPUType is self.optCPUType1:
        sSQL += 'AND quantity=1'
      elif self.oSelectedCPUType is self.optCPUTypeN:
        sSQL += 'AND quantity>1'
      sSQL += ' ORDER BY cpu_name'
      for row in self.database.select(sSQL, series):
        self.storeModels.append((
          len(row[0]) > 0 and row[0] or 'Unknown',
          row[0],
          row[1],
          row[2]
        ))
      # Automatically set the first item
      if len(self.storeModels) > 0:
        self.cboModels.set_active(0)

  def on_cboModels_changed(self, widget):
    # Update the label with the selected cpu score
    iSelectedRowIndex = self.cboModels.get_active()
    if iSelectedRowIndex >= 0:
      self.lblScore2.set_text(str(self.storeModels[iSelectedRowIndex][2]))

  def on_btnAdd_clicked(self, widget):
    # Add the selected item to the treeview data
    self.storeCompares.append((
      len(self.storeCompares) + 1,
      self.storeModels[self.cboModels.get_active()][3],
      self.storeBrands[self.cboBrands.get_active()][0],
      self.storeSeries[self.cboSeries.get_active()][0],
      self.storeModels[self.cboModels.get_active()][0],
      int(self.lblScore2.get_text()),
      int(self.lblScore2.get_text()) * 100 / self.lMaxScore,
    ))
    self.tvwCompares.set_cursor(len(self.storeCompares) - 1)

  def on_btnClear_clicked(self, widget):
    # Clear the treeview data
    self.storeCompares.clear()

  def on_btnAbout_clicked(self, widget):
    # Show the about dialog
    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(DIR_UI, 'about.glade'))
    dlgAbout = builder.get_object("dialogAbout")
    dlgAbout.set_program_name(APP_NAME)
    dlgAbout.set_version(APP_VERSION)
    dlgAbout.set_comments(APP_DESCRIPTION)
    dlgAbout.set_website(APP_URL)
    dlgAbout.set_copyright(APP_COPYRIGHT)
    dlgAbout.set_authors(['%s <%s>' % (APP_AUTHOR, APP_AUTHOR_EMAIL)]),
    dlgAbout.run()
    dlgAbout.destroy()
