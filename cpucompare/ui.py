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
from models import CPUCompareModelBrands
from models import CPUCompareModelSeries
from models import CPUCompareModelModels
import os.path

class CPUCompareUI(Gtk.Application):
  def __init__(self, database):
    Gtk.Application.__init__(self, application_id=APP_ID,
      flags=Gio.ApplicationFlags.FLAGS_NONE)
    self.loadUI(os.path.join(DIR_UI, 'cpucompare.glade'))
    self.database = database
    # Determine max score for relative score
    for row in self.database.select('SELECT MAX(score1) AS maxscore FROM cpu'):
      self.lMaxScore = row['maxscore']

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
    self.brands = CPUCompareModelBrands(builder.get_object('storeBrands'))
    self.series = CPUCompareModelSeries(builder.get_object('storeSeries'))
    self.models = CPUCompareModelModels(builder.get_object('storeModels'))
    self.storeCompares = builder.get_object('storeCompares')
    self.cboBrands = builder.get_object('cboBrands')
    self.cboSeries = builder.get_object('cboSeries')
    self.cboModels = builder.get_object('cboModels')
    self.lblScoreValue = builder.get_object('lblScoreValue')
    self.btnAdd = builder.get_object('btnAdd')
    self.btnClear = builder.get_object('btnClear')
    self.btnDelete = builder.get_object('btnDelete')
    self.tvwCompares = builder.get_object('tvwCompares')
    self.entrySearch = builder.get_object('entrySearch')
    self.entrycompletionSearch = builder.get_object('entrycompletionSearch')
    # The GtkEntryCompletion seems to have a bug which doesn't show the popup
    # at full height when the text column is set inside Glade instead of with
    # set_text_column method, so here I'm setting the text column again
    self.entrycompletionSearch.set_text_column(0)
    # Add a match function to find the input text in the whole text instead
    # of matching only the models starting with the input key
    self.entrycompletionSearch.set_match_func(
      self.entrycompletionSearch_match_func, self.models)
    # Connect signals from the glade file to the functions with the same name
    builder.connect_signals(self)

  def on_winMain_delete_event(self, widget, event):
    # Disconnect from the database and close
    self.database.close()
    Gtk.main_quit()

  def get_cpu_quantities(self):
    if self.oSelectedCPUType is self.optCPUType1:
      return 'quantity=1'
    elif self.oSelectedCPUType is self.optCPUTypeN:
      return 'quantity>1'
    else:
      return 'quantity>=1'

  def on_optCPUType_toggled(self, widget):
    # Do nothing if the signal is fired for the disabled state
    if widget.get_active():
      # Save the previous brand
      if self.cboBrands.get_active() >= 0:
        sPreviousBrand = self.brands.get_key(self.cboBrands.get_active())
      else:
        sPreviousBrand = None
      # Determine which brands to extract
      sSQL = 'SELECT DISTINCT brand FROM cpu WHERE '
      # Determine the CPU quantities
      self.oSelectedCPUType = widget
      sSQL += self.get_cpu_quantities()
      sSQL += ' ORDER BY brand'
      # Clear the model and load the brands
      self.brands.clear()
      # Retrieve the brands available for the selected CPU type
      for row in self.database.select(sSQL):
        # Add each row in the ListStore
        oLastTreeIter = self.brands.append(
          row['brand'] and (row['brand'], row['brand']) or ('Unknown', '')
        )
        # Restore the previously selected brand
        if sPreviousBrand == row['brand']:
          self.cboBrands.set_active_iter(oLastTreeIter)
      if self.cboBrands.get_active() < 0 and self.brands.count() > 0:
        self.cboBrands.set_active(0)

  def on_cboBrands_changed(self, widget):
    # Load the series for the requested brand
    self.series.clear()
    iSelectedRowIndex = self.cboBrands.get_active()
    if iSelectedRowIndex >= 0:
      lArguments = []
      sSQL = 'SELECT DISTINCT model1 FROM cpu WHERE '
      # Determine the CPU quantities
      sSQL += self.get_cpu_quantities()
      # Filter by brand
      sSQL += ' AND brand=?'
      lArguments.append(self.brands.get_key([iSelectedRowIndex]))
      sSQL += ' ORDER BY model1'
      for row in self.database.select(sSQL, *lArguments):
        self.series.append((
          row['model1'] and row['model1'] or 'Unknown',
          row['model1']
        ))
      # Automatically set the first item
      if self.series.count() > 0:
        self.cboSeries.set_active(0)

  def on_cboSeries_changed(self, widget):
    # Load the models for the requested series
    self.models.clear()
    # Retrieve the series
    iSelectedRowIndex = self.cboSeries.get_active()
    if iSelectedRowIndex >= 0:
      series = self.series.get_key(iSelectedRowIndex)
      iSelectedRowIndex = self.cboBrands.get_active()
      # There must be always a brand already selected to have a series chosen
      assert(iSelectedRowIndex >= 0)
      lArguments = []
      sSQL = 'SELECT cpu_name, score1, quantity, brand, model1 FROM cpu WHERE '
      # Determine the CPU quantities
      sSQL += self.get_cpu_quantities()
      # Filter by brand
      sSQL += ' AND brand=?'
      lArguments.append(self.brands.get_key(iSelectedRowIndex))
      # Filter by series
      sSQL += ' AND model1=?'
      lArguments.append(series)
      sSQL += ' ORDER BY cpu_name'
      for row in self.database.select(sSQL, *lArguments):
        self.models.append((
          row['cpu_name'] and row['cpu_name'] or 'Unknown',
          row['cpu_name'],
          row['score1'],
          row['quantity'],
          row['brand'],
          row['model1']
        ))
      # Automatically set the first item
      if self.models.count() > 0:
        self.cboModels.set_active(0)

  def on_cboModels_changed(self, widget):
    # Update the label with the selected cpu score
    iSelectedRowIndex = self.cboModels.get_active()
    if iSelectedRowIndex >= 0:
      self.lblScoreValue.set_text(str(self.models.get_score(iSelectedRowIndex)))

  def on_btnDelete_clicked(self, widget):
    # Remove the selected item from the treeview data
    (model, paths) = self.tvwCompares.get_selection().get_selected_rows()
    if len(paths) > 0:
      model.remove(model.get_iter(paths[0]))
      self.btnClear.set_sensitive(len(self.storeCompares) > 0)
      self.btnDelete.set_sensitive(len(self.storeCompares) > 0)

  def on_btnAdd_clicked(self, widget):
    # Add the selected item to the treeview data
    iSelectedRowIndex = self.cboModels.get_active()
    treeIter = self.models.model[iSelectedRowIndex]
    self.storeCompares.append((
      len(self.storeCompares) + 1,
      self.models.get_quantity(iSelectedRowIndex),
      self.models.get_brand(iSelectedRowIndex),
      self.models.get_series(iSelectedRowIndex),
      self.models.get_value(iSelectedRowIndex),
      self.models.get_score(iSelectedRowIndex),
      self.models.get_score(iSelectedRowIndex) * 100 / self.lMaxScore,
    ))
    self.tvwCompares.set_cursor(len(self.storeCompares) - 1)
    self.btnClear.set_sensitive(True)
    self.btnDelete.set_sensitive(True)

  def on_btnClear_clicked(self, widget):
    # Clear the treeview data
    self.storeCompares.clear()
    self.btnClear.set_sensitive(False)
    self.btnDelete.set_sensitive(False)

  def on_btnAbout_clicked(self, widget):
    # Show the about dialog
    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(DIR_UI, 'about.glade'))
    dlgAbout = builder.get_object("dialogAbout")
    dlgAbout.set_program_name(APP_NAME)
    dlgAbout.set_version('Version %s\nDatabase version %s' % (
      APP_VERSION, DATABASE_VERSION))
    dlgAbout.set_comments(APP_DESCRIPTION)
    dlgAbout.set_website(APP_URL)
    dlgAbout.set_copyright(APP_COPYRIGHT)
    dlgAbout.set_authors(['%s <%s>' % (APP_AUTHOR, APP_AUTHOR_EMAIL)]),
    dlgAbout.run()
    dlgAbout.destroy()

  def on_entrySearch_icon_press(self, widget, icon_pos, event):
    # The clear icon was activated
    if icon_pos == Gtk.EntryIconPosition.SECONDARY:
      self.entrySearch.set_text('')

  def entrycompletionSearch_match_func(self, widget, key, treeiter, model):
    # Search the item using the input text, irregardless of the text case
    # This will find all the items which contains the input key, not only
    # those which begins with such text
    return key in model.get_value(treeiter).lower()

  def on_entrycompletionSearch_match_selected(self, widget, model, treeiter):
    # Automatically select the matched model and add it to the compares list
    self.cboModels.set_active_iter(treeiter)
    self.btnAdd.clicked()
    # Clear the search text and ignore the default behavior to complete the item
    self.entrySearch.set_text('')
    return True
