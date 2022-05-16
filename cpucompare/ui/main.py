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

from gi.repository import Gtk

from cpucompare.constants import (APP_NAME,
                                  FILE_ICON,
                                  FILE_SETTINGS,
                                  FILE_WINDOWS_POSITION)
from cpucompare.functions import get_treeview_selected_row
from cpucompare.localize import text_gtk30
from cpucompare.settings import Settings
from cpucompare.database import ModelsDB
from cpucompare.ui.about import UIAbout
from cpucompare.ui.base import UIBase
from cpucompare.ui.shortcuts import UIShortcuts
from cpucompare.models.cpubrands import CPUBrands
from cpucompare.models.cpuseries import CPUSeries
from cpucompare.models.cpumodels import CPUModels
from cpucompare.models.cpuselections import CPUSelections

SECTION_WINDOW_NAME = 'main'


class UIMain(UIBase):
    def __init__(self, application, options):
        super().__init__(filename='main.ui')
        self.application = application
        self.folders = {}
        self.load_ui()
        self.settings = Settings(FILE_SETTINGS, True)
        self.positions = Settings(FILE_WINDOWS_POSITION, False)
        self.options = options
        self.positions.restore_window_position(window=self.ui.window,
                                               section=SECTION_WINDOW_NAME)
        # Load the brands, series and models
        self.database = ModelsDB()
        self.model_cpubrands = CPUBrands(self.ui.model_brands)
        self.model_cpuseries = CPUSeries(self.ui.model_series)
        self.model_cpumodels = CPUModels(self.ui.model_models)
        self.model_cpumodels_all = CPUModels(self.ui.model_models_all)
        self.model_selection = CPUSelections(self.ui.model_selections,
                                             self.database.get_max_score())
        self.database.load(self.model_cpumodels_all.add_data)
        # Add a match function to find the input text in the whole text instead
        # of matching only the models starting with the input key
        self.ui.entrycompletion_search.set_match_func(
            self.entrycompletion_search_match_func,
            self.model_cpumodels_all)

    def load_ui(self):
        """Load the interface UI"""
        # Initialize translations
        self.ui.action_about.set_label(text_gtk30('About'))
        self.ui.action_shortcuts.set_label(text_gtk30('Shortcuts'))
        # Initialize titles and tooltips
        self.set_titles()
        # Initialize Gtk.HeaderBar
        self.ui.header_bar.props.title = self.ui.window.get_title()
        self.ui.window.set_titlebar(self.ui.header_bar)
        self.set_buttons_icons(buttons=[self.ui.button_add,
                                        self.ui.button_remove,
                                        self.ui.button_clear,
                                        self.ui.button_find,
                                        self.ui.button_about,
                                        self.ui.button_options])
        # Set buttons with always show image
        for button in (self.ui.button_add, ):
            button.set_always_show_image(True)
        self.set_buttons_style_suggested_action(buttons=[self.ui.button_add])
        # Set various properties
        self.ui.window.set_title(APP_NAME)
        self.ui.window.set_icon_from_file(str(FILE_ICON))
        self.ui.window.set_application(self.application)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def run(self):
        """Show the UI"""
        self.ui.window.show_all()
        for brand in self.database.get_brands(cpu_quantity=1):
            self.model_cpubrands.add_data(brand)
        if len(self.model_cpubrands) > 0:
            self.ui.combo_brands.set_active(0)
        self.ui.combo_brands.grab_focus()

    def do_add_cpu_model_to_compares(self, item):
        """Add a InfoCPUModel item to the compares list"""
        self.model_selection.add_data(item)
        self.ui.action_clear.set_sensitive(True)

    def on_window_delete_event(self, widget, event):
        """Close the application by closing the main window"""
        self.ui.action_quit.emit('activate')

    def on_action_about_activate(self, action):
        """Show the about dialog"""
        dialog = UIAbout(self.ui.window)
        dialog.show()
        dialog.destroy()

    def on_action_shortcuts_activate(self, action):
        """Show the shortcuts dialog"""
        dialog = UIShortcuts(self.ui.window)
        dialog.show()

    def on_action_quit_activate(self, action):
        """Save the settings and close the application"""
        self.database.close()
        self.positions.save_window_position(
            self.ui.window, SECTION_WINDOW_NAME)
        self.positions.save()
        self.settings.save()
        self.ui.window.destroy()
        self.application.quit()

    def on_action_options_menu_activate(self, widget):
        """Open the options menu"""
        self.ui.button_options.emit('clicked')

    def on_action_add_activate(self, action):
        """Add the selected CPUModel to the selections list"""
        treeiter = self.ui.combo_models.get_active_iter()
        if treeiter:
            item = self.model_cpumodels.get_info_cpumodel(
                name=self.model_cpumodels.get_key(treeiter),
                quantity=self.model_cpumodels.get_quantity(treeiter))
            self.do_add_cpu_model_to_compares(item)

    def on_action_remove_activate(self, action):
        """Remove the selected CPUModel from the selections list"""
        treeiter = get_treeview_selected_row(self.ui.treeview_selections)
        if treeiter:
            self.model_selection.remove(treeiter)

    def on_action_clear_activate(self, action):
        """Clear the selections list"""
        self.model_selection.clear()
        self.ui.action_clear.set_sensitive(False)

    def on_action_find_toggled(self, action):
        """Show and hide the search entry"""
        status = self.ui.action_find.get_active()
        self.ui.revealer_find.set_reveal_child(status)
        if status:
            # Grab focus when search is enabled
            self.ui.entry_cputype_search.grab_focus()
        elif self.ui.window.get_focus() is self.ui.entry_cputype_search:
            # Set focus on the next widget if the focus was on the search entry
            self.ui.combo_brands.grab_focus()

    def on_action_find_close_activate(self, action):
        """Close the search"""
        self.ui.action_find.set_active(False)

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
            for series in self.database.get_series(cpu_quantity=1,
                                                   brand_name=selected_brand):
                new_iter = self.model_cpuseries.add_data(series)
                if series.name == selected_series:
                    treeiter = new_iter
            if len(self.model_cpuseries) > 0:
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
            for model in self.database.get_models(cpu_quantity=1,
                                                  brand_name=selected_brand,
                                                  series_name=selected_series):
                new_iter = self.model_cpumodels.add_data(model)
                if (model.name == selected_model and not treeiter):
                    treeiter = new_iter
            if len(self.model_cpumodels) > 0:
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

    def on_entry_cputype_search_activate(self, widget):
        """Clear the entry search field when ENTER was pressed"""
        self.ui.entry_cputype_search.set_text('')

    def on_entry_cputype_search_icon_press(self, widget, icon_pos, event):
        """The clear icon was activated"""
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            self.ui.entry_cputype_search.activate()

    def on_entrycompletion_search_match_selected(self, widget, model,
                                                 treeiter):
        """Add the selected treeiter to the selected CPU models"""
        item = self.model_cpumodels_all.get_info_cpumodel(
            name=self.model_cpumodels_all.get_key(treeiter),
            quantity=self.model_cpumodels_all.get_quantity(treeiter))
        self.do_add_cpu_model_to_compares(item)
        # Clear the search text and ignore the default behavior
        self.ui.entry_cputype_search.activate()
        return True

    def entrycompletion_search_match_func(self, widget, key, treeiter, model):
        """Search the item using the input text, regardless of the text case
        This will find all the items which contains the input key, not only
        those which begins with such text"""
        return key in model.get_key(treeiter).lower()

    def on_treeview_selections_selection_changed(self, widget):
        """Enable or disable the buttons when a selection is changed"""
        self.ui.action_remove.set_sensitive(
            get_treeview_selected_row(self.ui.treeview_selections) is not None)
        self.ui.action_clear.set_sensitive(len(self.model_selection) > 0)
