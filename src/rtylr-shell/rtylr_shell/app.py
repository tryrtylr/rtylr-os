"""GTK shell for launching and recovering a primary business application."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import shlex
import sys
import threading
import time
from typing import Any, Callable

from . import actions
from .config import ConfigError, ConfigStore, DEFAULT_CONFIG, Paths, StateStore
from .diagnostics import HealthItem, collect_health
from .ipc import CommandServer, send_command
from .security import hash_pin, valid_pin, verify_pin
from .supervisor import AppSupervisor, SupervisorSnapshot

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - exercised on appliance
    Gdk = GLib = Gtk = None
    GTK_IMPORT_ERROR: Exception | None = exc
else:
    GTK_IMPORT_ERROR = None


LOGGER = logging.getLogger("rtylr-shell")


def _add_class(widget: Any, *names: str) -> Any:
    context = widget.get_style_context()
    for name in names:
        context.add_class(name)
    return widget


def _set_feedback(widget: Any, text: str, style: str) -> None:
    context = widget.get_style_context()
    for name in ("muted", "error-label", "success-label"):
        context.remove_class(name)
    context.add_class(style)
    widget.set_text(text)


def _label(text: str, *classes: str, xalign: float = 0.0, wrap: bool = True) -> Any:
    label = Gtk.Label(label=text)
    label.set_xalign(xalign)
    label.set_line_wrap(wrap)
    for name in classes:
        _add_class(label, name)
    return label


def _button(text: str, callback: Callable[..., Any], style: str = "secondary") -> Any:
    button = Gtk.Button(label=text)
    _add_class(button, style)
    button.connect("clicked", callback)
    button.set_can_focus(True)
    return button


class RtylrShell:
    def __init__(self, initial_command: str | None = None):
        self.paths = Paths.runtime()
        self.config_store = ConfigStore(self.paths)
        self.state_store = StateStore(self.paths)
        self.config_error = ""
        try:
            self.config = self.config_store.load()
        except ConfigError as exc:
            self.config = deepcopy(DEFAULT_CONFIG)
            self.config_error = str(exc)
        try:
            self.state_store.load()
        except ConfigError as exc:
            self.config_error = f"{self.config_error}\n{exc}".strip()

        self._configure_logging()
        self.supervisor = AppSupervisor(self.config["application"], self.paths.application_log)
        self.support_code = actions.support_code(self.paths.device_id)
        self.initial_command = initial_command
        self.active_view = ""
        self.pin_buffer = ""
        self.pin_failures = 0
        self.pin_locked_until = 0.0
        self.health_refreshing = False
        self.last_health_refresh = 0.0
        self.last_status = self.supervisor.status
        self.app_mode_requested = False
        self.pending_admin_action: str | None = None

        self._load_style()
        self.window = Gtk.Window(title="Rtylr OS")
        self.window.set_wmclass("rtylr-shell", "RtylrShell")
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.connect("delete-event", lambda *_args: True)
        self.window.connect("key-press-event", self._on_key_press)
        self.window.fullscreen()

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(180)
        self.window.add(self.stack)

        self.clock_labels: list[Any] = []
        self.health_widgets: dict[str, tuple[Any, Any, Any]] = {}
        self._build_setup_view()
        self._build_dashboard_view()
        self._build_pin_view()
        self._build_recovery_view()
        self._build_hot_control()
        self._set_config_error(self.config_error)

        self.command_server = CommandServer(
            lambda command: GLib.idle_add(self._handle_command, command)
        )
        self.command_server.start()
        GLib.timeout_add_seconds(1, self._tick)

    def _configure_logging(self) -> None:
        if LOGGER.handlers:
            return
        LOGGER.setLevel(logging.INFO)
        try:
            shell_log = self.paths.application_log.with_name("shell.log")
            shell_log.parent.mkdir(parents=True, exist_ok=True)
            handler: logging.Handler = RotatingFileHandler(
                shell_log, maxBytes=1_000_000, backupCount=2, encoding="utf-8"
            )
        except OSError:
            handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        LOGGER.addHandler(handler)

    def _load_style(self) -> None:
        provider = Gtk.CssProvider()
        style_path = Path(__file__).with_name("style.css")
        css = style_path.read_text(encoding="utf-8")
        css = css.replace("#7c5cff", self.config["brand"]["accent"])
        provider.load_from_data(css.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _topbar(self, title: str | None = None) -> Any:
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        _add_class(bar, "topbar")
        brand = _label(self.config["brand"]["wordmark"], "brand", xalign=0.0, wrap=False)
        bar.pack_start(brand, False, False, 0)
        if title:
            divider = _label("/", "topbar-divider", wrap=False)
            bar.pack_start(divider, False, False, 0)
            bar.pack_start(_label(title, "topbar-title", wrap=False), False, False, 0)
        clock = _label("", "clock", xalign=1.0, wrap=False)
        self.clock_labels.append(clock)
        bar.pack_end(clock, False, False, 0)
        return bar

    def _screen(self) -> Any:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        _add_class(root, "screen")
        return root

    def _card(self, spacing: int = 16) -> Any:
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
        _add_class(card, "card")
        return card

    def _field(self, label_text: str, placeholder: str = "") -> tuple[Any, Any]:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        box.pack_start(_label(label_text, "field-label", wrap=False), False, False, 0)
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_activates_default(False)
        box.pack_start(entry, False, False, 0)
        return box, entry

    def _build_setup_view(self) -> None:
        root = self._screen()
        root.pack_start(self._topbar("First setup"), False, False, 0)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=28)
        _add_class(body, "page-body")
        root.pack_start(body, True, True, 0)

        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        _add_class(hero, "setup-hero")
        hero.pack_start(
            _label("THE OPERATING SYSTEM FOR YOUR BUSINESS", "eyebrow"), False, False, 0
        )
        hero.pack_start(
            _label("Set up the workspace your team runs on.", "hero-title"),
            False,
            False,
            0,
        )
        hero.pack_start(
            _label(
                "Rtylr opens your primary business app, keeps the device healthy, and gives your team a fast recovery path when software, hardware, or connectivity goes wrong.",
                "hero-copy",
            ),
            False,
            False,
            0,
        )
        feature_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for text in (
            "Touch-first and keyboard complete",
            "Protected recovery and system actions",
            "Bounded crash recovery—no infinite restart loops",
        ):
            feature_box.pack_start(_label(f"●  {text}", "feature-line"), False, False, 0)
        hero.pack_start(feature_box, False, False, 12)
        self.setup_health = _label("Checking device readiness…", "muted")
        hero.pack_end(self.setup_health, False, False, 0)
        body.pack_start(hero, True, True, 0)

        form = self._card(14)
        _add_class(form, "setup-card")
        form.pack_start(_label("Choose your primary business app", "card-title"), False, False, 0)
        form.pack_start(
            _label("The executable can be installed now or provisioned later.", "muted"),
            False,
            False,
            0,
        )
        name_box, self.setup_name_entry = self._field("Display name", "Business workspace")
        command_box, self.setup_command_entry = self._field(
            "Command", "/opt/my-business/app --kiosk"
        )
        self.setup_name_entry.set_text(self.config["application"]["name"])
        self.setup_command_entry.set_text(shlex.join(self.config["application"]["command"]))
        form.pack_start(name_box, False, False, 0)
        form.pack_start(command_box, False, False, 0)

        pin_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        pin_box, self.setup_pin_entry = self._field("Admin PIN", "4–8 digits")
        confirm_box, self.setup_pin_confirm_entry = self._field("Confirm PIN", "Repeat PIN")
        for entry in (self.setup_pin_entry, self.setup_pin_confirm_entry):
            entry.set_visibility(False)
            entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
            entry.set_max_length(8)
        pin_row.pack_start(pin_box, True, True, 0)
        pin_row.pack_start(confirm_box, True, True, 0)
        form.pack_start(pin_row, False, False, 0)

        self.setup_error = _label("", "error-label")
        form.pack_start(self.setup_error, False, False, 0)
        finish = _button("Finish setup", self._finish_setup, "primary")
        form.pack_end(finish, False, False, 0)
        body.pack_end(form, False, False, 0)

        self.stack.add_named(root, "setup")

    def _build_dashboard_view(self) -> None:
        root = self._screen()
        root.pack_start(self._topbar(), False, False, 0)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        _add_class(body, "center-body")
        root.pack_start(body, True, True, 0)

        self.dashboard_pill = _label("READY", "status-pill", "status-neutral", xalign=0.5, wrap=False)
        body.pack_start(self.dashboard_pill, False, False, 0)
        self.dashboard_title = _label("Your business is ready", "hero-title", xalign=0.5)
        body.pack_start(self.dashboard_title, False, False, 0)
        self.dashboard_message = _label(
            "Rtylr will open the primary app configured for this business.",
            "hero-copy",
            xalign=0.5,
        )
        self.dashboard_message.set_justify(Gtk.Justification.CENTER)
        body.pack_start(self.dashboard_message, False, False, 0)
        self.dashboard_config_error = _label("", "error-label", xalign=0.5)
        body.pack_start(self.dashboard_config_error, False, False, 0)

        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        actions_box.set_halign(Gtk.Align.CENTER)
        actions_box.pack_start(
            _button("Open business app", self._start_app, "primary"), False, False, 0
        )
        actions_box.pack_start(
            _button("Recovery & settings", lambda *_: self._request_recovery(), "secondary"),
            False,
            False,
            0,
        )
        body.pack_start(actions_box, False, False, 14)
        body.pack_end(
            _label(f"Support code  {self.support_code}", "support-code", xalign=0.5, wrap=False),
            False,
            False,
            0,
        )
        self.stack.add_named(root, "dashboard")

    def _build_pin_view(self) -> None:
        root = self._screen()
        root.pack_start(self._topbar("Admin access"), False, False, 0)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        _add_class(body, "pin-body")
        root.pack_start(body, True, True, 0)
        body.pack_start(_label("Enter admin PIN", "hero-title", xalign=0.5), False, False, 0)
        body.pack_start(
            _label("Recovery and system settings are protected from accidental changes.", "muted", xalign=0.5),
            False,
            False,
            0,
        )
        self.pin_dots = _label("○ ○ ○ ○", "pin-dots", xalign=0.5, wrap=False)
        body.pack_start(self.pin_dots, False, False, 10)
        self.pin_error = _label("", "error-label", xalign=0.5)
        body.pack_start(self.pin_error, False, False, 0)

        keypad = Gtk.Grid(column_spacing=10, row_spacing=10)
        keypad.set_halign(Gtk.Align.CENTER)
        for index, digit in enumerate("123456789"):
            button = _button(digit, lambda _button, value=digit: self._pin_digit(value), "pin-button")
            keypad.attach(button, index % 3, index // 3, 1, 1)
        keypad.attach(_button("Cancel", lambda *_: self._close_admin(), "pin-action"), 0, 3, 1, 1)
        keypad.attach(_button("0", lambda *_: self._pin_digit("0"), "pin-button"), 1, 3, 1, 1)
        keypad.attach(_button("⌫", lambda *_: self._pin_delete(), "pin-action"), 2, 3, 1, 1)
        body.pack_start(keypad, False, False, 6)
        body.pack_start(_button("Unlock", lambda *_: self._pin_submit(), "primary"), False, False, 4)
        self.stack.add_named(root, "pin")

    def _build_recovery_view(self) -> None:
        root = self._screen()
        topbar = self._topbar("Recovery & settings")
        topbar.pack_end(
            _button("Return to business app", lambda *_: self._close_admin(), "ghost"),
            False,
            False,
            0,
        )
        root.pack_start(topbar, False, False, 0)

        notebook = Gtk.Notebook()
        _add_class(notebook, "recovery-tabs")
        notebook.set_scrollable(True)
        root.pack_start(notebook, True, True, 0)

        status_page = Gtk.ScrolledWindow()
        status_page.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        status_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        _add_class(status_content, "page-body")
        status_page.add(status_content)
        self.recovery_config_error = _label("", "error-label")
        status_content.pack_start(self.recovery_config_error, False, False, 0)
        app_card = self._card(14)
        heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        self.recovery_app_title = _label("Business app status", "card-title")
        self.recovery_app_pill = _label("CHECKING", "status-pill", "status-neutral", xalign=0.5)
        heading.pack_start(self.recovery_app_title, True, True, 0)
        heading.pack_end(self.recovery_app_pill, False, False, 0)
        app_card.pack_start(heading, False, False, 0)
        self.recovery_app_message = _label("Checking the configured application…", "muted")
        app_card.pack_start(self.recovery_app_message, False, False, 0)
        app_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        app_actions.pack_start(
            _button("Restart app", self._restart_app, "primary"), False, False, 0
        )
        app_actions.pack_start(
            _button("Stop app", self._stop_app, "secondary"), False, False, 0
        )
        app_card.pack_start(app_actions, False, False, 0)
        status_content.pack_start(app_card, False, False, 0)

        status_content.pack_start(_label("Device health", "section-title"), False, False, 0)
        health_grid = Gtk.Grid(column_spacing=14, row_spacing=14)
        for index, (key, title) in enumerate(
            (("network", "Network"), ("storage", "Storage"), ("printing", "Printing"), ("usb", "USB devices"))
        ):
            card = self._card(8)
            _add_class(card, "health-card", "status-neutral")
            item_title = _label(title, "health-title")
            item_summary = _label("Checking…", "health-summary")
            item_detail = _label("", "muted")
            card.pack_start(item_title, False, False, 0)
            card.pack_start(item_summary, False, False, 0)
            card.pack_start(item_detail, False, False, 0)
            self.health_widgets[key] = (card, item_summary, item_detail)
            health_grid.attach(card, index % 2, index // 2, 1, 1)
        status_content.pack_start(health_grid, False, False, 0)
        refresh = _button("Run checks again", lambda *_: self._refresh_health(), "secondary")
        refresh.set_halign(Gtk.Align.START)
        status_content.pack_start(refresh, False, False, 0)
        notebook.append_page(status_page, _label("Status", "tab-label", wrap=False))

        settings_page = Gtk.ScrolledWindow()
        settings_page.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        settings_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        _add_class(settings_content, "page-body")
        settings_page.add(settings_content)
        settings_card = self._card(14)
        settings_card.pack_start(_label("Primary business app", "card-title"), False, False, 0)
        settings_card.pack_start(
            _label("Rtylr executes this command directly and never through a shell.", "muted"),
            False,
            False,
            0,
        )
        name_box, self.settings_name_entry = self._field("Display name")
        command_box, self.settings_command_entry = self._field("Command")
        settings_card.pack_start(name_box, False, False, 0)
        settings_card.pack_start(command_box, False, False, 0)
        auto_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        auto_row.pack_start(_label("Launch automatically after login", "field-label"), True, True, 0)
        self.settings_auto_switch = Gtk.Switch()
        auto_row.pack_end(self.settings_auto_switch, False, False, 0)
        settings_card.pack_start(auto_row, False, False, 0)
        self.settings_result = _label("", "muted")
        settings_card.pack_start(self.settings_result, False, False, 0)
        save_button = _button("Save app settings", self._save_settings, "primary")
        save_button.set_halign(Gtk.Align.START)
        settings_card.pack_start(save_button, False, False, 0)
        settings_content.pack_start(settings_card, False, False, 0)
        notebook.append_page(settings_page, _label("App settings", "tab-label", wrap=False))

        system_page = Gtk.ScrolledWindow()
        system_page.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        system_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        _add_class(system_content, "page-body")
        system_page.add(system_content)
        recovery_card = self._card(14)
        recovery_card.pack_start(_label("Recovery actions", "card-title"), False, False, 0)
        recovery_card.pack_start(
            _label("Use these actions only when the status page identifies a problem.", "muted"),
            False,
            False,
            0,
        )
        system_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        system_actions.pack_start(
            _button("Reconnect network", self._reconnect_network, "secondary"), False, False, 0
        )
        system_actions.pack_start(
            _button("Reboot device", lambda *_: self._confirm_power_action("reboot"), "secondary"),
            False,
            False,
            0,
        )
        system_actions.pack_start(
            _button("Shut down", lambda *_: self._confirm_power_action("poweroff"), "danger"),
            False,
            False,
            0,
        )
        recovery_card.pack_start(system_actions, False, False, 0)
        self.system_result = _label("", "muted")
        recovery_card.pack_start(self.system_result, False, False, 0)
        system_content.pack_start(recovery_card, False, False, 0)

        pin_card = self._card(14)
        pin_card.pack_start(_label("Admin PIN", "card-title"), False, False, 0)
        pin_card.pack_start(
            _label("Change the PIN used to protect recovery and system actions.", "muted"),
            False,
            False,
            0,
        )
        pin_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        new_pin_box, self.new_pin_entry = self._field("New PIN", "4–8 digits")
        confirm_pin_box, self.confirm_pin_entry = self._field("Confirm PIN", "Repeat PIN")
        for entry in (self.new_pin_entry, self.confirm_pin_entry):
            entry.set_visibility(False)
            entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
            entry.set_max_length(8)
        pin_row.pack_start(new_pin_box, True, True, 0)
        pin_row.pack_start(confirm_pin_box, True, True, 0)
        pin_card.pack_start(pin_row, False, False, 0)
        self.pin_change_result = _label("", "muted")
        pin_card.pack_start(self.pin_change_result, False, False, 0)
        change_pin = _button("Change admin PIN", self._change_pin, "secondary")
        change_pin.set_halign(Gtk.Align.START)
        pin_card.pack_start(change_pin, False, False, 0)
        system_content.pack_start(pin_card, False, False, 0)

        log_card = self._card(12)
        log_heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        log_heading.pack_start(_label("Recent business app log", "card-title"), True, True, 0)
        log_heading.pack_end(_label(self.support_code, "support-code", wrap=False), False, False, 0)
        log_card.pack_start(log_heading, False, False, 0)
        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        log_scroll.set_min_content_height(210)
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.set_monospace(True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.CHAR)
        log_scroll.add(self.log_view)
        log_card.pack_start(log_scroll, True, True, 0)
        system_content.pack_start(log_card, True, True, 0)
        notebook.append_page(system_page, _label("System", "tab-label", wrap=False))

        self.stack.add_named(root, "recovery")

    def _build_hot_control(self) -> None:
        self.hot_window = Gtk.Window(title="Rtylr control")
        self.hot_window.set_wmclass("rtylr-control", "RtylrControl")
        self.hot_window.set_decorated(False)
        self.hot_window.set_resizable(False)
        self.hot_window.set_keep_above(True)
        self.hot_window.set_skip_taskbar_hint(True)
        self.hot_window.set_skip_pager_hint(True)
        self.hot_window.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.hot_window.set_default_size(54, 54)
        self.hot_window.set_accept_focus(False)
        button = Gtk.Button(label="R")
        _add_class(button, "hot-control")
        button.set_tooltip_text("Open Rtylr recovery")
        button.connect("clicked", lambda *_: self._request_recovery())
        self.hot_window.add(button)
        self.hot_window.connect("delete-event", lambda *_args: True)

    def start(self) -> None:
        self.window.show_all()
        self._refresh_health()
        if not self.state_store.setup_complete:
            self._show_view("setup")
        else:
            self._show_dashboard()
            if self.config["application"]["auto_start"]:
                GLib.timeout_add(700, self._start_app)
        if self.initial_command:
            GLib.idle_add(self._handle_command, self.initial_command)

    def run(self) -> int:
        self.start()
        try:
            Gtk.main()
        finally:
            self.command_server.close()
            self.supervisor.stop()
        return 0

    def _show_view(self, name: str) -> None:
        self.active_view = name
        self.stack.set_visible_child_name(name)
        self.hot_window.hide()
        self.window.show_all()
        self.window.present()
        self.window.fullscreen()

    def _show_dashboard(self) -> None:
        self._show_view("dashboard")
        self._update_app_status(self.supervisor.snapshot())

    def _start_app(self, *_args: Any) -> bool:
        self.app_mode_requested = True
        started = self.supervisor.start(reset_failures=True)
        snapshot = self.supervisor.snapshot()
        self._update_app_status(snapshot)
        if started:
            GLib.timeout_add(1300, self._enter_app_mode)
        else:
            self._show_dashboard()
        return False

    def _enter_app_mode(self) -> bool:
        if not self.supervisor.running or self.active_view in {"recovery", "pin", "setup"}:
            return False
        self.window.hide()
        if self.config["ui"]["touch_control"]:
            self.hot_window.show_all()
            GLib.idle_add(self._position_hot_control)
        self.active_view = "app"
        self.app_mode_requested = False
        return False

    def _position_hot_control(self) -> bool:
        screen = self.hot_window.get_screen()
        monitor = screen.get_primary_monitor()
        if monitor < 0:
            monitor = 0
        geometry = screen.get_monitor_geometry(monitor)
        self.hot_window.move(geometry.x + geometry.width - 66, geometry.y + 12)
        return False

    def _request_recovery(self) -> None:
        self._request_admin()

    def _request_admin(self, action: str | None = None) -> None:
        if not self.state_store.setup_complete:
            self.pending_admin_action = None
            self._show_view("setup")
            return
        self.pending_admin_action = action
        if self.state_store.get("admin_pin"):
            self.pin_buffer = ""
            self.pin_error.set_text("")
            self._update_pin_dots()
            self._show_view("pin")
        else:
            self._complete_admin_action()

    def _complete_admin_action(self) -> None:
        action = self.pending_admin_action
        self.pending_admin_action = None
        if action in {"restart-app", "restart-pos"}:
            self._show_dashboard()
            self._restart_app()
        else:
            self._show_recovery()

    def _show_recovery(self) -> None:
        self.settings_name_entry.set_text(self.config["application"]["name"])
        self.settings_command_entry.set_text(shlex.join(self.config["application"]["command"]))
        self.settings_auto_switch.set_active(self.config["application"]["auto_start"])
        self.settings_result.set_text("")
        self.system_result.set_text("")
        self.new_pin_entry.set_text("")
        self.confirm_pin_entry.set_text("")
        _set_feedback(self.pin_change_result, "", "muted")
        self.log_view.get_buffer().set_text(actions.read_log_tail(self.paths.application_log))
        self._show_view("recovery")
        self._refresh_health()
        self._update_app_status(self.supervisor.snapshot())

    def _close_admin(self) -> None:
        self.pin_buffer = ""
        self.pending_admin_action = None
        if self.supervisor.running:
            self.active_view = "dashboard"
            self._enter_app_mode()
        else:
            self._show_dashboard()

    def _pin_digit(self, digit: str) -> None:
        if time.monotonic() < self.pin_locked_until or len(self.pin_buffer) >= 8:
            return
        self.pin_buffer += digit
        self.pin_error.set_text("")
        self._update_pin_dots()

    def _pin_delete(self) -> None:
        self.pin_buffer = self.pin_buffer[:-1]
        self._update_pin_dots()

    def _update_pin_dots(self) -> None:
        filled = "● " * len(self.pin_buffer)
        empty = "○ " * max(0, 4 - len(self.pin_buffer))
        self.pin_dots.set_text((filled + empty).strip())

    def _pin_submit(self) -> None:
        remaining = self.pin_locked_until - time.monotonic()
        if remaining > 0:
            self.pin_error.set_text(f"Try again in {int(remaining) + 1} seconds.")
            return
        if verify_pin(self.pin_buffer, self.state_store.get("admin_pin")):
            self.pin_failures = 0
            self.pin_buffer = ""
            self._complete_admin_action()
            return
        self.pin_buffer = ""
        self.pin_failures += 1
        self._update_pin_dots()
        if self.pin_failures >= 5:
            self.pin_failures = 0
            self.pin_locked_until = time.monotonic() + 30
            self.pin_error.set_text("Too many attempts. Try again in 30 seconds.")
        else:
            self.pin_error.set_text("Incorrect PIN.")

    def _parse_app_fields(self, name: str, command_text: str) -> dict[str, Any]:
        name = name.strip()
        if not name:
            raise ConfigError("Enter a business app display name.")
        try:
            command = shlex.split(command_text)
        except ValueError as exc:
            raise ConfigError(f"Invalid command: {exc}") from exc
        if not command or not Path(command[0]).is_absolute():
            raise ConfigError("The app command must start with an absolute executable path.")
        updated = deepcopy(self.config)
        updated["application"]["name"] = name
        updated["application"]["command"] = command
        updated["application"]["working_directory"] = str(Path(command[0]).parent)
        return updated

    def _finish_setup(self, *_args: Any) -> None:
        pin = self.setup_pin_entry.get_text()
        confirmation = self.setup_pin_confirm_entry.get_text()
        try:
            updated = self._parse_app_fields(
                self.setup_name_entry.get_text(), self.setup_command_entry.get_text()
            )
            if pin != confirmation:
                raise ConfigError("The PIN confirmation does not match.")
            if not valid_pin(pin):
                raise ConfigError("Use a PIN containing four to eight digits.")
            self.config_store.save(updated)
            self.state_store.set("admin_pin", hash_pin(pin))
            self.state_store.set("setup_complete", True)
            self.state_store.save()
        except (ConfigError, OSError, ValueError) as exc:
            self.setup_error.set_text(str(exc))
            return
        self.config = updated
        self.supervisor.update_config(self.config["application"])
        self._set_config_error("")
        self.setup_error.set_text("")
        self._show_dashboard()
        if self.config["application"]["auto_start"]:
            GLib.timeout_add(500, self._start_app)

    def _save_settings(self, *_args: Any) -> None:
        try:
            updated = self._parse_app_fields(
                self.settings_name_entry.get_text(), self.settings_command_entry.get_text()
            )
            updated["application"]["auto_start"] = self.settings_auto_switch.get_active()
            self.config_store.save(updated)
        except (ConfigError, OSError) as exc:
            _set_feedback(self.settings_result, str(exc), "error-label")
            return
        self.config = updated
        self.supervisor.update_config(self.config["application"])
        self._set_config_error("")
        _set_feedback(self.settings_result, "Business app settings saved.", "success-label")

    def _change_pin(self, *_args: Any) -> None:
        pin = self.new_pin_entry.get_text()
        confirmation = self.confirm_pin_entry.get_text()
        try:
            if pin != confirmation:
                raise ConfigError("The PIN confirmation does not match.")
            if not valid_pin(pin):
                raise ConfigError("Use a PIN containing four to eight digits.")
            self.state_store.set("admin_pin", hash_pin(pin))
            self.state_store.save()
        except (ConfigError, OSError, ValueError) as exc:
            _set_feedback(self.pin_change_result, str(exc), "error-label")
            return
        self.new_pin_entry.set_text("")
        self.confirm_pin_entry.set_text("")
        _set_feedback(self.pin_change_result, "Admin PIN changed.", "success-label")

    def _set_config_error(self, message: str) -> None:
        self.config_error = message.strip()
        display = f"Configuration issue: {self.config_error}" if self.config_error else ""
        self.setup_error.set_text(display)
        self.dashboard_config_error.set_text(display)
        self.recovery_config_error.set_text(display)

    def _restart_app(self, *_args: Any) -> None:
        self.app_mode_requested = True
        if self.supervisor.restart():
            self._update_app_status(self.supervisor.snapshot())
            GLib.timeout_add(1200, self._enter_app_mode)
        else:
            self._update_app_status(self.supervisor.snapshot())

    def _stop_app(self, *_args: Any) -> None:
        self.supervisor.stop()
        self.app_mode_requested = False
        self._update_app_status(self.supervisor.snapshot())

    def _refresh_health(self) -> None:
        if self.health_refreshing:
            return
        self.health_refreshing = True

        def worker() -> None:
            result = collect_health()
            GLib.idle_add(self._apply_health, result)

        threading.Thread(target=worker, name="rtylr-health", daemon=True).start()

    def _apply_health(self, items: list[HealthItem]) -> bool:
        self.health_refreshing = False
        self.last_health_refresh = time.monotonic()
        okay = 0
        for item in items:
            widgets = self.health_widgets.get(item.key)
            if widgets:
                card, summary, detail = widgets
                context = card.get_style_context()
                for name in ("status-ok", "status-warning", "status-error", "status-neutral"):
                    context.remove_class(name)
                context.add_class(f"status-{item.status}")
                summary.set_text(item.summary)
                detail.set_text(item.detail)
            if item.status == "ok":
                okay += 1
        self.setup_health.set_text(f"Device readiness: {okay} of {len(items)} checks healthy")
        return False

    def _update_app_status(self, snapshot: SupervisorSnapshot) -> None:
        mapping = {
            "running": ("RUNNING", "status-ok"),
            "restarting": ("RECOVERING", "status-warning"),
            "missing": ("SETUP NEEDED", "status-error"),
            "failed": ("NEEDS ATTENTION", "status-error"),
            "stopped": ("STOPPED", "status-neutral"),
            "idle": ("READY", "status-neutral"),
        }
        text, style = mapping.get(snapshot.status, (snapshot.status.upper(), "status-neutral"))
        for pill in (self.dashboard_pill, self.recovery_app_pill):
            context = pill.get_style_context()
            for name in ("status-ok", "status-warning", "status-error", "status-neutral"):
                context.remove_class(name)
            context.add_class(style)
            pill.set_text(text)
        self.dashboard_title.set_text(self.config["application"]["name"])
        self.dashboard_message.set_text(snapshot.message)
        self.recovery_app_title.set_text(self.config["application"]["name"])
        self.recovery_app_message.set_text(snapshot.message)

    def _run_action(self, label: str, action: Callable[[], actions.ActionResult]) -> None:
        self.system_result.set_text(f"{label}…")

        def worker() -> None:
            result = action()
            GLib.idle_add(
                self.system_result.set_text,
                result.message or (f"{label} complete." if result.ok else f"{label} failed."),
            )
            GLib.idle_add(self._refresh_health)

        threading.Thread(target=worker, name="rtylr-action", daemon=True).start()

    def _reconnect_network(self, *_args: Any) -> None:
        self._run_action("Reconnecting network", actions.reconnect_network)

    def _confirm_power_action(self, action_name: str) -> None:
        is_reboot = action_name == "reboot"
        verb = "Reboot" if is_reboot else "Shut down"
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text=f"{verb} this device?",
        )
        dialog.format_secondary_text(
            "The business app will be stopped and any unsaved work may be lost."
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button(verb, Gtk.ResponseType.OK)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            self._run_action(verb, actions.reboot if is_reboot else actions.poweroff)

    def _handle_command(self, command: str) -> bool:
        if command == "show-recovery":
            self._request_recovery()
        elif command in {"restart-app", "restart-pos"}:
            self._request_admin("restart-app")
        elif command == "show-shell":
            self._show_dashboard()
        elif command == "quit":
            Gtk.main_quit()
        return False

    def _on_key_press(self, _widget: Any, event: Any) -> bool:
        if self.active_view != "pin":
            return False
        key = Gdk.keyval_name(event.keyval) or ""
        if len(key) == 1 and key.isdigit():
            self._pin_digit(key)
            return True
        if key in {"BackSpace", "Delete"}:
            self._pin_delete()
            return True
        if key in {"Return", "KP_Enter"}:
            self._pin_submit()
            return True
        if key == "Escape":
            self._close_admin()
            return True
        return False

    def _tick(self) -> bool:
        now = datetime.now().strftime("%H:%M")
        for clock in self.clock_labels:
            clock.set_text(now if self.config["ui"]["show_clock"] else "")

        snapshot = self.supervisor.poll()
        self._update_app_status(snapshot)
        if self.last_status == "restarting" and snapshot.status == "running":
            self.app_mode_requested = True
            GLib.timeout_add(1000, self._enter_app_mode)
        elif self.last_status == "running" and snapshot.status != "running":
            self.app_mode_requested = True
            if self.active_view == "app":
                self._show_dashboard()
        self.last_status = snapshot.status

        if time.monotonic() - self.last_health_refresh >= 10:
            self._refresh_health()
        if self.active_view == "recovery":
            self.log_view.get_buffer().set_text(actions.read_log_tail(self.paths.application_log))
        return True


def _requested_command(arguments: argparse.Namespace) -> str | None:
    if arguments.recovery:
        return "show-recovery"
    if arguments.restart_app or arguments.restart_pos:
        return "restart-app"
    if arguments.show_shell:
        return "show-shell"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rtylr OS appliance shell")
    parser.add_argument("--recovery", action="store_true", help="open protected recovery")
    parser.add_argument(
        "--restart-app", action="store_true", help="restart the primary business app"
    )
    parser.add_argument("--restart-pos", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--show-shell", action="store_true", help="show the shell dashboard")
    arguments = parser.parse_args(argv)
    command = _requested_command(arguments)
    if command and send_command(command):
        return 0
    if GTK_IMPORT_ERROR is not None:
        print(f"Rtylr shell requires GTK 3 and PyGObject: {GTK_IMPORT_ERROR}", file=sys.stderr)
        return 1
    initialized, _remaining = Gtk.init_check([])
    if not initialized:
        print("Rtylr shell could not initialize the graphical display.", file=sys.stderr)
        return 1
    shell = RtylrShell(initial_command=command)
    return shell.run()
