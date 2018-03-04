import paho.mqtt.client as mqtt
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject
from libs.TopicViews import TextView
from config.config import views, connection


class HeaderBarWindow(Gtk.Window):

    def __init__(self, topicViews, connection):
        self.topicViews = topicViews
        self.connection = connection
        Gtk.Window.__init__(self, title="MqttDashboad")
        self.set_border_width(10)
        self.set_default_size(400, 200)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "MqttDashboad"
        hb.props.subtitle = connection["server"]
        self.set_titlebar(hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="list-add-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.on_add_button_clicked)
        hb.pack_end(button)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(5)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(flowbox)

        self.add(scrolled)

        for topicView in self.topicViews:
            flowbox.add(topicView)
        self.show_all()

        self.init_popover()

        self.client = mqtt.Client()
        self.client.username_pw_set(connection["user"], connection["password"])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(connection["server"], connection["port"])
        self.client.loop_start()

    def init_popover(self):
        self.popover = Gtk.Popover()
        vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        vbox.pack_start(Gtk.Button.new_with_label("new ToggleView"), False, True, 10)
        vbox.pack_start(Gtk.Button.new_with_label("new TextView"), False, True, 10)
        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)

    def on_add_button_clicked(self, widget):
        self.popover.set_relative_to(widget)
        self.popover.show_all()
        print("asd")

    def on_connect(self, client, userdata, flags, rc):
        for topicView in self.topicViews:
            topicView.set_client(self.client)
            client.subscribe(topicView.get_topic())

    def on_message(self, client, userdata, msg):
        msg_str = msg.payload.decode('utf8')
        for topicView in self.topicViews:
            if topicView.get_topic() == msg.topic:
                topicView.on_message(userdata, msg_str, msg)


settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", True)
win = HeaderBarWindow(views, connection)
win.connect("delete-event", Gtk.main_quit)
Gtk.main()
