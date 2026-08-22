from pathlib import Path
import tempfile
import unittest
from unittest import mock

from rtylr_shell.diagnostics import CommandResult, network_health, printing_health, storage_health, usb_health


class DiagnosticTests(unittest.TestCase):
    def test_connected_network(self):
        result = network_health(runner=lambda _command, _timeout: CommandResult(0, "connected"))
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.summary, "Connected")

    def test_offline_network(self):
        result = network_health(runner=lambda _command, _timeout: CommandResult(0, "disconnected"))
        self.assertEqual(result.status, "error")

    def test_low_storage_is_error(self):
        usage = shutil_usage(total=100 * 1024**3, used=99 * 1024**3, free=1 * 1024**3)
        with mock.patch("rtylr_shell.diagnostics.shutil.disk_usage", return_value=usage):
            self.assertEqual(storage_health().status, "error")

    def test_printer_count(self):
        def runner(command, _timeout):
            if command == ["lpstat", "-r"]:
                return CommandResult(0, "scheduler is running")
            return CommandResult(0, "printer receipt is idle\nprinter kitchen is idle")

        result = printing_health(runner=runner)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.summary, "2 printers ready")

    def test_paused_printer_is_not_reported_ready(self):
        def runner(command, _timeout):
            if command == ["lpstat", "-r"]:
                return CommandResult(0, "scheduler is running")
            return CommandResult(
                0,
                "printer receipt is idle\nprinter kitchen disabled since Monday",
            )

        result = printing_health(runner=runner)
        self.assertEqual(result.status, "warning")
        self.assertEqual(result.summary, "1 ready, 1 paused")

    def test_usb_devices_are_counted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "1-1"
            first.mkdir()
            (first / "idVendor").write_text("1234", encoding="utf-8")
            (root / "usb1").mkdir()
            result = usb_health(root)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.summary, "1 detected")

    def test_usb_hubs_are_not_counted_as_peripherals(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            hub = root / "usb1"
            hub.mkdir()
            (hub / "idVendor").write_text("1d6b", encoding="utf-8")
            (hub / "bDeviceClass").write_text("09", encoding="utf-8")
            result = usb_health(root)
        self.assertEqual(result.status, "warning")
        self.assertEqual(result.summary, "No peripherals detected")


def shutil_usage(total, used, free):
    return (total, used, free)


if __name__ == "__main__":
    unittest.main()
