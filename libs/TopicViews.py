import gi
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject, Gdk


class TopicView(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.get_style_context().add_class("TopicView")

        # Setup Css
        css = Gtk.CssProvider()
        css.load_from_path("./libs/TopicViews.css")
        context = Gtk.StyleContext()
        context.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.props.halign = Gtk.Align.CENTER

        self.show_all()

    def on_message(self, userdata, payload, msg):
        pass

    def get_topic(self):
        pass

    def set_client(self, client):
        self.client = client

    def send_message(self, msg):
        self.client.publish(self.get_topic(), msg)


class DefaultTopicView(TopicView):
    def __init__(self, topic, name):
        super().__init__()
        self.topic = topic
        self.name = name

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.last_update_time = time.time()

        self.name_label = Gtk.Label(name)
        self.name_label.props.halign = Gtk.Align.CENTER
        self.time_label = Gtk.Label("---")
        self.update_time_label()
        self.grid.attach(self.name_label, 0, 0, 4, 1)
        self.grid.attach(self.create_content_view(), 0, 1, 4, 4)
        self.grid.attach(self.time_label, 0, 5, 4, 1)
        self.grid.connect("button-press-event", self.on_clicked)
        GObject.timeout_add(500, self.update_time_label)

    def format_time_interval(self, interval_secs):
        if interval_secs < 60:
            return "{} s".format(round(interval_secs))
        elif interval_secs < 60*60:
            return "{} min".format(round(interval_secs / 60))
        elif interval_secs < 60*60*60:
            return "{} h".format(round(interval_secs / 60*60))
        else:
            return "{} Days".format(round(interval_secs / 60*60*24))

    def update_time_label(self):
        self.time_label.set_text(
            self.format_time_interval(time.time() - self.last_update_time))
        return True

    def create_content_view(self):
        pass

    def get_topic(self):
        return self.topic

    def on_clicked(self, widget, event):
        print("clicked")

    def on_message(self, userdata, payload, msg):
        self.handle_message(userdata, payload, msg)
        self.last_update_time = time.time()
        self.update_time_label()

    def handle_message(self, userdata, payload, msg):
        pass


class TextView(DefaultTopicView):
    def __init__(self, topic, name):
        super().__init__(topic, name)

    def create_content_view(self):
        self.label = Gtk.Label("")
        return self.label

    def handle_message(self, userdata, payload, msg):
        self.label.set_text(payload)


class CheckBoxView(DefaultTopicView):
    def __init__(self, topic, name, on_value="1", off_value="0"):
        super().__init__(topic, name)
        self.on_value = on_value
        self.off_value = off_value

    def create_content_view(self):
        self.checkbox = Gtk.CheckButton("")
        self.checkbox.props.halign = Gtk.Align.CENTER
        self.checkbox.get_style_context().add_class("mqtt-checkbox")
        self.checkbox.connect("toggled", self.switch)
        return self.checkbox

    def handle_message(self, userdata, payload, msg):
        if payload == self.on_value:
            self.checkbox.set_active(True)
        else:
            self.checkbox.set_active(False)

    def switch(self, button):
        if button.get_active():
            self.send_message(self.on_value)
        else:
            self.send_message(self.off_value)

