
from gettext import gettext as _

from gi.repository import Gtk, Gdk, GLib

from .settings import settings
from . import app_info
from . import fontlib


class MainWindow(Gtk.ApplicationWindow):

    _DND_URI = 0
    _DND_LIST = [Gtk.TargetEntry.new('text/uri-list', 0, _DND_URI)]

    def __init__(self, app):
        super().__init__(title=app_info.TITLE, application=app)

        self._app = app
        self.connect('window-state-event', self._on_window_state_event)
        self.connect('delete-event', self._on_delete_event)

        self.drag_dest_set(
            Gtk.DestDefaults.ALL, self._DND_LIST, Gdk.DragAction.COPY)
        self.connect('drag-data-received', self._on_drag_data_received)

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(grid)

        main_menu = self._create_menubar()
        grid.add(main_menu)

        self._library = fontlib.FontLib()
        grid.add(self._library)

        grid.show_all()

    def _create_menubar(self):
        ag = Gtk.AccelGroup()
        self.add_accel_group(ag)

        menubar = Gtk.MenuBar()

        # File.

        file_menu = Gtk.Menu()
        mi_file = Gtk.MenuItem.new_with_mnemonic(_('_File'))
        mi_file.set_submenu(file_menu)
        menubar.append(mi_file)

        mi_quit = Gtk.MenuItem(
            label=_('Quit'),
            action_name='app.quit')
        key, mod = Gtk.accelerator_parse('<Control>Q')
        mi_quit.add_accelerator(
            'activate', ag, key, mod, Gtk.AccelFlags.VISIBLE)
        file_menu.append(mi_quit)

        # Help.

        help_menu = Gtk.Menu()
        mi_help = Gtk.MenuItem.new_with_mnemonic(_('_Help'))
        mi_help.set_submenu(help_menu)
        menubar.append(mi_help)

        mi_about = Gtk.MenuItem(
            label=_('About'),
            action_name='app.about')
        help_menu.append(mi_about)

        return menubar

    def _on_drag_data_received(self, window, context, x, y, selection,
                               target, time):
        if target == self._DND_URI:
            self._library.add_fonts(
                (GLib.filename_from_uri(uri)[0] for uri in
                 selection.get_uris() if uri.startswith('file://')))
        context.finish(True, False, time)

    def _on_window_state_event(self, window, event):
        settings['window_maximized'] = bool(
            event.new_window_state & Gdk.WindowState.MAXIMIZED)

    def _on_delete_event(self, window, event):
        self._app.quit()

    def save_state(self):
        self._library.save_state()

        settings['window_x'], settings['window_y'] = self.get_position()
        settings['window_width'], settings['window_height'] = self.get_size()

    def load_state(self):
        try:
            if settings['window_maximized']:
                self.maximize()
            else:
                self.move(settings['window_x'], settings['window_y'])
                self.resize(
                    settings['window_width'], settings['window_height'])
        except (KeyError, TypeError):
            pass

        self._library.load_state()
