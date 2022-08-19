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

import logging

from gi.repository import Gtk

from cpucompare.constants import (APP_NAME,
                                  FILE_ICON,
                                  FILE_SETTINGS)
from cpucompare.database import ModelsDB
from cpucompare.functions import get_treeview_selected_row
from cpucompare.localize import text
from cpucompare.models.cpubrands import CPUBrands
from cpucompare.models.cpumodels import CPUModels
from cpucompare.models.cpuselections import CPUSelections
from cpucompare.models.cpuseries import CPUSeries
from cpucompare.settings import Settings
from cpucompare.ui.about import UIAbout
from cpucompare.ui.base import UIBase
from cpucompare.ui.shortcuts import UIShortcuts

SECTION_WINDOW_NAME = 'main'


class UIMain(UIBase):
    def __init__(self, application, options):
        """Prepare the main window"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='main.ui')
        # Initialize members
        self.application = application
        self.options = options
        # Load settings
        self.settings = Settings(filename=FILE_SETTINGS,
                                 case_sensitive=True)
        self.settings.load_preferences()
        self.settings_map = {}
        # Load UI
        self.load_ui()
        # Prepare the models
        self.database = ModelsDB()
        self.model_cpubrands = CPUBrands(self.ui.model_brands)
        self.model_cpuseries = CPUSeries(self.ui.model_series)
        self.model_cpumodels = CPUModels(self.ui.model_models)
        self.model_cpumodels_all = CPUModels(self.ui.model_models_all)
        self.model_selection = CPUSelections(self.ui.model_selections,
                                             self.database.get_max_score())
        # Add a match function to search the input text in the whole text
        # instead of matching only the models starting with the input key
        self.ui.entrycompletion_search.set_match_func(
            self.do_entrycompletion_search_match,
            self.model_cpumodels_all)
        # Complete initialization
        self.startup()

    def load_ui(self):
        """Load the interface UI"""
        logging.debug(f'{self.__class__.__name__} load UI')
        # Initialize titles and tooltips
        self.set_titles()
        self.ui.entry_cputype_search.set_icon_tooltip_text(
            Gtk.EntryIconPosition.PRIMARY,
            self.ui.entry_cputype_search.get_tooltip_text())
        self.ui.entry_cputype_search.set_icon_tooltip_text(
            Gtk.EntryIconPosition.SECONDARY, text('Clear'))
        # Initialize Gtk.HeaderBar
        self.ui.header_bar.props.title = self.ui.window.get_title()
        self.ui.window.set_titlebar(self.ui.header_bar)
        self.set_buttons_icons(buttons=[self.ui.button_add,
                                        self.ui.button_remove,
                                        self.ui.button_clear,
                                        self.ui.button_search,
                                        self.ui.button_about,
                                        self.ui.button_options])
        # Set buttons with always show image
        for button in [self.ui.button_add]:
            button.set_always_show_image(True)
        # Set buttons as suggested
        self.set_buttons_style_suggested_action(
            buttons=[self.ui.button_add])
        # Set various properties
        self.ui.window.set_title(APP_NAME)
        self.ui.window.set_icon_from_file(str(FILE_ICON))
        self.ui.window.set_application(self.application)
        # Connect signals from the UI file to the functions with the same name
        self.ui.connect_signals(self)

    def startup(self):
        """Complete initialization"""
        logging.debug(f'{self.__class__.__name__} startup')
        self.database.load(cb_add_row=self.model_cpumodels_all.add_data)
        # Load settings
        for setting_name, action in self.settings_map.items():
            action.set_active(self.settings.get_preference(
                option=setting_name))
        # Restore the saved size and position
        self.settings.restore_window_position(window=self.ui.window,
                                              section=SECTION_WINDOW_NAME)

    def run(self):
        """Show the UI"""
        logging.debug(f'{self.__class__.__name__} run')
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

    def do_entrycompletion_search_match(self, widget, key, treeiter, model):
        """Search the item using the input text, regardless of the text case
        This will search all the items which contains the input key, not only
        those which begins with such text"""
        return key in model.get_key(treeiter).lower()

    def on_action_about_activate(self, widget):
        """Show the information dialog"""
        dialog = UIAbout(parent=self.ui.window,
                         settings=self.settings,
                         options=self.options)
        dialog.show()
        dialog.destroy()

    def on_action_shortcuts_activate(self, widget):
        """Show the shortcuts dialog"""
        dialog = UIShortcuts(parent=self.ui.window,
                             settings=self.settings,
                             options=self.options)
        dialog.show()

    def on_action_quit_activate(self, widget):
        """Save the settings and close the application"""
        logging.debug(f'{self.__class__.__name__} quit')
        self.settings.save_window_position(window=self.ui.window,
                                           section=SECTION_WINDOW_NAME)
        self.settings.save()
        self.ui.window.destroy()
        self.database.close()
        self.application.quit()

    def on_action_options_menu_activate(self, widget):
        """Open the options menu"""
        self.ui.button_options.clicked()

    def on_action_add_activate(self, widget):
        """Add the selected CPUModel to the selections list"""
        treeiter = self.ui.combo_models.get_active_iter()
        if treeiter:
            item = self.model_cpumodels.get_info_cpumodel(
                name=self.model_cpumodels.get_key(treeiter),
                quantity=self.model_cpumodels.get_quantity(treeiter))
            self.do_add_cpu_model_to_compares(item)

    def on_action_remove_activate(self, widget):
        """Remove the selected CPUModel from the selections list"""
        treeiter = get_treeview_selected_row(self.ui.treeview_selections)
        if treeiter:
            self.model_selection.remove(treeiter)

    def on_action_clear_activate(self, widget):
        """Clear the selections list"""
        self.model_selection.clear()
        self.ui.action_clear.set_sensitive(False)

    def on_action_search_toggled(self, widget):
        """Show and hide the search entry"""
        status = self.ui.action_search.get_active()
        self.ui.revealer_search.set_reveal_child(status)
        if status:
            # Grab focus when search is enabled
            self.ui.entry_cputype_search.grab_focus()
        elif self.ui.window.get_focus() is self.ui.entry_cputype_search:
            # Set focus on the next widget if the focus was on the search entry
            self.ui.combo_brands.grab_focus()

    def on_action_search_close_activate(self, widget):
        """Close the search"""
        self.ui.action_search.set_active(False)

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
            selected_brand = (self.model_cpubrands.get_key(treeiter)
                              if treeiter
                              else None)
            # Save currently selected series
            treeiter = self.ui.combo_series.get_active_iter()
            selected_series = (self.model_cpuseries.get_key(treeiter)
                               if treeiter
                               else None)
            # Save currently selected model
            treeiter = self.ui.combo_models.get_active_iter()
            selected_model = (self.model_cpumodels.get_key(treeiter)
                              if treeiter
                              else None)
            # Clear previous series
            treeiter = None
            self.model_cpumodels.clear()
            for model in self.database.get_models(cpu_quantity=1,
                                                  brand_name=selected_brand,
                                                  series_name=selected_series):
                new_iter = self.model_cpumodels.add_data(model)
                if model.name == selected_model and not treeiter:
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

    def on_treeview_selections_selection_changed(self, widget):
        """Enable or disable the buttons when a selection is changed"""
        self.ui.action_remove.set_sensitive(
            get_treeview_selected_row(self.ui.treeview_selections) is not None)
        self.ui.action_clear.set_sensitive(len(self.model_selection) > 0)

    def on_window_delete_event(self, widget, event):
        """Close the application by closing the main window"""
        self.ui.action_quit.activate()
