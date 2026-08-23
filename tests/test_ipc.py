from pathlib import Path
import stat
import tempfile
import threading
import unittest

from rtylr_shell.ipc import ALLOWED_COMMANDS, CommandServer, send_command


class CommandChannelTests(unittest.TestCase):
    def test_local_command_round_trip_and_socket_permissions(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "shell.sock"
            received: list[str] = []
            delivered = threading.Event()

            def callback(command: str) -> None:
                received.append(command)
                delivered.set()

            server = CommandServer(callback, path)
            try:
                server.start()
            except PermissionError as exc:
                self.skipTest(f"Unix sockets are blocked by this test environment: {exc}")
            try:
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                self.assertTrue(send_command("show-recovery", path))
                self.assertTrue(delivered.wait(1.0))
                self.assertEqual(received, ["show-recovery"])
            finally:
                server.close()

            self.assertFalse(path.exists())

    def test_rejects_unknown_command(self):
        with self.assertRaises(ValueError):
            send_command("run-anything")

    def test_business_app_restart_keeps_legacy_alias(self):
        self.assertIn("restart-app", ALLOWED_COMMANDS)
        self.assertIn("restart-pos", ALLOWED_COMMANDS)


if __name__ == "__main__":
    unittest.main()
