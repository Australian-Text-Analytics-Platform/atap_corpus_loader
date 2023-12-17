import fnmatch
from glob import glob
from os.path import isdir, join

import panel
from panel import Row, Column
from panel.widgets import Button, MultiSelect, TextInput

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class FileSelectorWidget(AbstractWidget):
    def __init__(self, view_handler: AbstractWidget, controller: Controller, base_path: str):
        super().__init__()
        self.view_handler: AbstractWidget = view_handler
        self.controller: Controller = controller
        self.directory: str = base_path

        self.select_all_button = Button(name="Select all", width=95,
                                        button_style="solid", button_type="primary")
        self.select_all_button.on_click(self.select_all)

        self.filter_input = TextInput(placeholder="Filter displayed files (supports wildcard syntax)",
                                      sizing_mode='stretch_width')
        self.filter_input.param.watch(self._on_filter_change, ['value_input'])

        self.selector_widget = MultiSelect(size=20, sizing_mode='stretch_width')

        self.panel = Column(
            Row(self.select_all_button),
            Row(self.filter_input),
            Row(self.selector_widget),
            width=700)

        panel.state.add_periodic_callback(self.update_display, period=2000)
        self.update_display()
        self.select_all()

    def update_display(self):
        filter_str = f"*{self.filter_input.value_input}*"

        all_paths: list[str] = glob("**", root_dir=self.directory, recursive=True)
        filtered_paths: list[str] = fnmatch.filter(all_paths, filter_str)
        filtered_files: list[str] = [p for p in filtered_paths if not isdir(join(self.directory, p))]

        old_selected_files: list[str] = self.selector_widget.value.copy()
        filtered_selected_files: list[str] = [f for f in old_selected_files if f in filtered_files]

        loaded_corpus_files: list[str] = self.controller.get_loaded_corpus_files()
        loaded_meta_files: list[str] = self.controller.get_loaded_meta_files()

        filtered_files_dict = {}
        checkmark_symbol = "\U00002714"
        for file in filtered_files:
            full_path = join(self.directory, file)
            file_repr = file
            if full_path in loaded_corpus_files:
                file_repr += f" {checkmark_symbol} [corpus]"
            if full_path in loaded_meta_files:
                file_repr += f" {checkmark_symbol} [meta]"
            filtered_files_dict[file_repr] = file

        self.selector_widget.options = filtered_files_dict
        self.selector_widget.value = filtered_selected_files

    def _on_filter_change(self, *_):
        self.update_display()
        self.select_all()

    def select_all(self, *_):
        self.selector_widget.value = list(self.selector_widget.options.values())

    def get_selector_value(self) -> list[str]:
        return self.selector_widget.value
