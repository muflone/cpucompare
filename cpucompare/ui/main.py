##
#     Project: CPUCompare
# Description: A GTK+ application to make comparisons between CPU models
#      Author: Fabio Castelli <muflone@muflone.com>
#   Copyright: 2013-2022 Fabio Castelli
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
from gi.repository import Gdk
from gi.repository import Gio

from cpucompare.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION)
from cpucompare.functions import get_treeview_selected_row
from cpucompare.localize import text, _
import cpucompare.settings as settings
from cpucompare.gtkbuilder_loader import GtkBuilderLoader
from cpucompare.database import ModelsDB
from cpucompare.localize import strip_underline

from cpucompare.ui.about import UIAbout
from cpucompare.ui.shortcuts import UIShortcuts

from cpucompare.models.cpubrands import CPUBrands
from cpucompare.models.cpuseries import CPUSeries
from cpucompare.models.cpumodels import CPUModels
from cpucompare.models.cpuselections import CPUSelections

SECTION_WINDOW_NAME = 'main'


class UIMain(object):
    def __init__(self, application):
        self.application = application
        # Load settings
        settings.settings = settings.Settings(FILE_SETTINGS, False)
        settings.positions = settings.Settings(FILE_WINDOWS_POSITION, False)
        self.folders = {}
        self.loadUI()
        # Load the brands, series and models
        self.database = ModelsDB()
        self.ui.progressbar_loading.current_items = 0
        self.ui.progressbar_loading.max_items = (
            self.database.get_models_count())
        self.ui.progressbar_loading.set_fraction(0.0)
        self.database.load(self.cb_add_new_model)
        # Prepares the models
        self.model_cpubrands = CPUBrands(self.ui.store_brands)
        self.model_cpuseries = CPUSeries(self.ui.store_series)
        self.model_cpumodels = CPUModels(self.ui.store_models)
        self.model_cpumodels_all = CPUModels(self.ui.store_models_all)
        self.model_selection = CPUSelections(self.ui.store_selections,
                                             self.database.get_max_score())
        # Add a match function to find the input text in the whole text instead
        # of matching only the models starting with the input key
        self.ui.entrycompletion_search.set_match_func(
            self.entrycompletion_search_match_func,
            self.model_cpumodels_all)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.window_main, SECTION_WINDOW_NAME)

    def loadUI(self):
        """Load the interface UI"""
        self.ui = GtkBuilderLoader('main.ui')
        self.ui.window_main.set_application(self.application)
        self.ui.window_main.set_title(APP_NAME)

        # FIXME: move this checks into functions
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            label = widget.get_label()
            if not label:
                label = widget.get_short_label()
            widget.set_label(text(label))
            widget.set_short_label(label)
        # Initialize labels
        for widget in self.ui.get_objects_by_type(Gtk.Label):
            widget.set_label(text(widget.get_label()))
        # Initialize toolbuttons
        for widget in self.ui.get_objects_by_type(Gtk.ToolButton):
            widget.set_label(text(widget.get_label()))
        # Initialize Gtk.TreeViewColumn
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        # Initialize tooltips
        for gtk_type in (Gtk.Button, Gtk.ToolButton):
            for widget in self.ui.get_objects_by_type(gtk_type):
                action = widget.get_related_action()
                if action:
                    widget.set_tooltip_text(
                        strip_underline(action.get_label()))
                else:
                    widget.set_tooltip_text(
                        strip_underline(widget.get_label()))
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def run(self):
        """Show the UI"""
        self.ui.window_main.show_all()
        self.ui.option_cputype_single.emit('toggled')
        self.ui.combo_brands.grab_focus()

    def on_window_main_delete_event(self, widget, event):
        """Save the settings and close the application"""
        self.database.close()
        settings.positions.save_window_position(
            self.ui.window_main, SECTION_WINDOW_NAME)
        settings.positions.save()
        settings.settings.save()
        self.application.quit()

    def on_action_application_about_activate(self, action):
        """Show the about dialog"""
        dialog = UIAbout(self.ui.window_main)
        dialog.show()
        dialog.destroy()

    def on_action_application_shortcuts_activate(self, action):
        """Show the shortcuts dialog"""
        dialog = UIShortcuts(self.ui.window_main)
        dialog.show()

    def on_action_application_quit_activate(self, action):
        """Close the application by closing the main window"""
        event = Gdk.Event()
        event.key.type = Gdk.EventType.DELETE
        self.ui.window_main.event(event)

    def on_option_cputype_toggled(self, widget):
        """Change the CPU type and reload the CPU brands list"""
        if widget.get_active():
            # Save currently selected brand
            selected_brand = None
            treeiter = self.ui.combo_brands.get_active_iter()
            if treeiter:
                selected_brand = self.model_cpubrands.get_key(treeiter)
            # Clear previous brands
            treeiter = None
            self.model_cpubrands.clear()
            for brand in self.database.get_brands(self.get_cpu_quantity()):
                new_iter = self.model_cpubrands.add_data(brand)
                if brand.name == selected_brand:
                    treeiter = new_iter
            if self.model_cpubrands.count() > 0:
                if treeiter:
                    # Restore the previously selected brand
                    self.ui.combo_brands.set_active_iter(treeiter)
                else:
                    # Select the first brand if needed
                    self.ui.combo_brands.set_active(0)

    def on_combo_brands_changed(self, widget):
        """Change the CPU brand and reload the CPU series list"""
        treeiter = self.ui.combo_brands.get_active_iter()
        if treeiter:
            selected_brand = self.model_cpubrands.get_key(treeiter)
            # Save currently selected series
            selected_series = None
            treeiter = self.ui.combo_series.get_active_iter()
            if treeiter:
                selected_series = self.model_cpuseries.get_key(treeiter)
            # Clear previous series
            treeiter = None
            self.model_cpuseries.clear()
            for series in self.database.get_series(self.get_cpu_quantity(),
                                                   selected_brand):
                new_iter = self.model_cpuseries.add_data(series)
                if series.name == selected_series:
                    treeiter = new_iter
            if self.model_cpuseries.count() > 0:
                if treeiter:
                    # Restore the previously selected series
                    self.ui.combo_series.set_active_iter(treeiter)
                else:
                    # Select the first series if needed
                    self.ui.combo_series.set_active(0)

    def on_combo_series_changed(self, widget):
        """Change the CPU series and reload the CPU models list"""
        treeiter = self.ui.combo_series.get_active_iter()
        if treeiter:
            # Save currently selected brand
            treeiter = self.ui.combo_brands.get_active_iter()
            if treeiter:
                selected_brand = self.model_cpubrands.get_key(treeiter)
            # Save currently selected series
            selected_series = None
            treeiter = self.ui.combo_series.get_active_iter()
            if treeiter:
                selected_series = self.model_cpuseries.get_key(treeiter)
            # Save currently selected model
            selected_model = None
            treeiter = self.ui.combo_models.get_active_iter()
            if treeiter:
                selected_model = self.model_cpumodels.get_key(treeiter)
            # Clear previous series
            treeiter = None
            self.model_cpumodels.clear()
            for model in self.database.get_models(self.get_cpu_quantity(),
                                                  selected_brand,
                                                  selected_series):
                new_iter = self.model_cpumodels.add_data(model)
                if (model.name == selected_model and not treeiter):
                    treeiter = new_iter
            if self.model_cpumodels.count() > 0:
                if treeiter:
                    # Restore the previously selected model
                    self.ui.combo_models.set_active_iter(treeiter)
                else:
                    # Select the first model if needed
                    self.ui.combo_models.set_active(0)

    def on_combo_models_changed(self, widget):
        """Update the score value for the selected CPU Model"""
        treeiter = self.ui.combo_models.get_active_iter()
        if treeiter:
            score = self.model_cpumodels.get_score(treeiter)
            self.ui.label_score_value.set_text(str(score))

    def on_action_selections_add_activate(self, action):
        """Add the selected CPUModel to the selections list"""
        treeiter = self.ui.combo_models.get_active_iter()
        if treeiter:
            item = self.model_cpumodels.get_info_cpumodel(
                name=self.model_cpumodels.get_key(treeiter),
                quantity=self.model_cpumodels.get_quantity(treeiter))
            self.add_cpu_model_to_compares(item)

    def on_action_selections_remove_activate(self, action):
        """Remove the selected CPUModel from the selections list"""
        treeiter = get_treeview_selected_row(self.ui.treeview_selections)
        if treeiter:
            self.model_selection.remove(treeiter)

    def on_action_selections_clear_activate(self, action):
        """Clear the selections list"""
        self.model_selection.clear()
        self.ui.action_selections_clear.set_sensitive(False)

    def on_entrycompletion_search_match_selected(self, widget, model,
                                                 treeiter):
        """Add the selected treeiter to the selected CPU models"""
        item = self.model_cpumodels_all.get_info_cpumodel(
            name=self.model_cpumodels_all.get_key(treeiter),
            quantity=self.model_cpumodels_all.get_quantity(treeiter))
        self.add_cpu_model_to_compares(item)
        # Clear the search text and ignore the default behavior
        self.ui.entry_cputype_search.activate()
        return True

    def on_entry_cputype_search_activate(self, widget):
        """Clear the entry search field when ENTER was pressed"""
        self.ui.entry_cputype_search.set_text('')

    def on_entry_cputype_search_icon_press(self, widget, icon_pos, event):
        """The clear icon was activated"""
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            self.ui.entry_cputype_search.activate()

    def cb_add_new_model(self, model):
        """Add a new ModelInfo object to the CPU Models list"""
        self.ui.progressbar_loading.current_items += 1
        total = self.ui.progressbar_loading.max_items
        current = self.ui.progressbar_loading.current_items
        self.model_cpumodels_all.add_data(model)
        self.ui.progressbar_loading.set_fraction(float(current) / total)
        # Hide the GtkProgress after the load is complete
        if current == total:
            self.ui.progressbar_loading.set_visible(False)
            self.ui.entry_cputype_search.set_sensitive(True)

    def get_cpu_quantity(self):
        """
        Return a value for CPU quantity:
        0 for All CPU types
        1 for Single CPU types
        2 for Multiple CPU types
        """
        if self.ui.option_cputype_single.get_active():
            result = 1
        elif self.ui.option_cputype_multiple.get_active():
            result = 2
        else:
            result = 0
        return result

    def entrycompletion_search_match_func(self, widget, key, treeiter, model):
        """Search the item using the input text, regardless of the text case
        This will find all the items which contains the input key, not only
        those which begins with such text"""
        return key in model.get_key(treeiter).lower()

    def add_cpu_model_to_compares(self, item):
        """Add a the InfoCPUModel item to the compares list"""
        self.model_selection.add_data(item)
        self.ui.treeview_selections.set_cursor(
            self.model_selection.count() - 1)
        self.ui.action_selections_clear.set_sensitive(True)

    def on_treeview_selections_selection_changed(self, widget):
        """Enable or disable the remove button when a selection is made"""
        self.ui.action_selections_remove.set_sensitive(
            get_treeview_selected_row(self.ui.treeview_selections) is not None)
