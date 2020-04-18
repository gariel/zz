from typing import Callable, Dict, List
import traceback


class zWidget:
    def __init__(self, widget):
        self._widget = widget
        self._events: Dict[str, "zEvent"] = {}

    def __getattribute__(self, name):
        if not name.startswith("_"):
            if name.startswith("on_"):
                event = name[3:]
                if event not in self._events:
                    self._events[event] = zEvent(event, self)
                return self._events[event]

            gget = f"get_{name}"
            if hasattr(self._widget, gget):
                return getattr(self._widget, gget)()

        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)

        sset = f"set_{name}"
        if hasattr(self._widget, sset):
            getattr(self._widget, sset)(value)
        else:
            super().__setattr__(name, value)


class zEvent:
    def __init__(self, name: str, widget: zWidget):
        self.name = name
        self._widget = widget
        self._widget._widget.connect(name, self._fire)

        self._registered: List[Callable[[zWidget], None]] = []
        self._mapping: Dict[str, Callable[[zWidget], None]] = {}


    def _fire(self, _wid):
        for callback in self._registered:
            callback(self._widget)


    def add(self, callback: Callable[[zWidget], None], key: str=""):
        self._registered.append(callback)
        if key:
            self._mapping[key] = callback

    def remove(self, key: str):
        if key in self._mapping:
            callback = self._mapping.pop(key)
            self._registered.remove(callback)


class zFixedEventHandler(dict):
    def __init__(self, window):
        self._window = window

    def get(self, name, _):
        def fire(wid):
            zw = self._window._widget_map[id(wid)]
            
            if not hasattr(self._window, name):
                print(":::: No mapped callback '{}' for widget '{}' on '{}'"
                    .format(name, ident, self._window.name))
                return

            method = getattr(self._window, name)
            method(zw)
        return fire


class zWindow:
    def __init__(self, gladefile, windowname):
        self.name = windowname
        self._glade = gladefile

    def __do_build__(self, gtk):
        self._builder = gtk.Builder()
        self._builder.add_from_file(f"{self._glade}.glade")

        window = self._builder.get_object(self.name)
        self._builder.connect_signals(zFixedEventHandler(self))

        self._window = zWidget(window)
        self._widget_map = {}
        self._rec(window)
        self.__build__()

    def __build__(self):
        pass

    def _rec(self, wid):
        name = wid.get_name()

        z = zWidget(wid)
        setattr(self, name, z)
        self._widget_map[id(wid)] = z
        
        if hasattr(wid, "get_children"):
            children = wid.get_children()
            for c in children:
                self._rec(c)
        elif hasattr(wid, "get_child"):
            c = wid.get_child()
            if c:
                self._rec(c)


    def show(self):
        self._window._widget.show_all()


class zApp:
    def run(self, window: zWindow):
        try:
            self._run(window)
        except:
            traceback.print_exc()

    def _run(self, window: zWindow):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        window.__do_build__(Gtk)
        window.show()
        window._window.on_destroy.add(Gtk.main_quit)

        Gtk.main()

