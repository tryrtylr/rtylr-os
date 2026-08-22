from pathlib import Path
import subprocess
import tempfile
import unittest

from rtylr_shell.supervisor import PosSupervisor


class FakeProcess:
    next_pid = 100

    def __init__(self):
        self.returncode = None
        self.pid = FakeProcess.next_pid
        FakeProcess.next_pid += 1

    def poll(self):
        return self.returncode

    def terminate(self):
        self.returncode = 0

    def kill(self):
        self.returncode = -9

    def wait(self, timeout=None):
        if self.returncode is None:
            raise subprocess.TimeoutExpired("fake", timeout)
        return self.returncode


class FakePopen:
    def __init__(self):
        self.processes = []
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        process = FakeProcess()
        self.processes.append(process)
        return process


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.clock_value = 100.0
        self.popen = FakePopen()
        self.config = {
            "name": "Store POS",
            "command": ["/opt/store/pos", "--kiosk"],
            "working_directory": "/opt/store",
            "restart": {
                "max_attempts": 3,
                "window_seconds": 60,
                "backoff_seconds": [1, 2],
            },
        }
        self.supervisor = PosSupervisor(
            self.config,
            Path(self.temporary.name) / "pos.log",
            clock=lambda: self.clock_value,
            popen_factory=self.popen,
            executable_check=lambda _path: True,
        )

    def tearDown(self):
        self.supervisor.stop()
        self.temporary.cleanup()

    def test_command_is_passed_as_array_without_shell(self):
        self.assertTrue(self.supervisor.start())
        command, options = self.popen.calls[0]
        self.assertEqual(command, ["/opt/store/pos", "--kiosk"])
        self.assertNotIn("shell", options)
        self.assertEqual(self.supervisor.snapshot().status, "running")

    def test_crash_uses_backoff_and_restarts(self):
        self.supervisor.start()
        self.popen.processes[-1].returncode = 2
        snapshot = self.supervisor.poll()
        self.assertEqual(snapshot.status, "restarting")
        self.assertEqual(snapshot.next_restart_seconds, 1)
        self.clock_value += 1
        self.assertEqual(self.supervisor.poll().status, "running")
        self.assertEqual(len(self.popen.processes), 2)

    def test_repeated_crashes_stop_the_loop(self):
        self.supervisor.start()
        for delay in (1, 2):
            self.popen.processes[-1].returncode = 9
            self.supervisor.poll()
            self.clock_value += delay
            self.supervisor.poll()
        self.popen.processes[-1].returncode = 9
        snapshot = self.supervisor.poll()
        self.assertEqual(snapshot.status, "failed")
        self.assertIn("repeatedly", snapshot.message)

    def test_missing_executable_is_actionable(self):
        supervisor = PosSupervisor(
            self.config,
            Path(self.temporary.name) / "missing.log",
            executable_check=lambda _path: False,
        )
        self.assertFalse(supervisor.start())
        self.assertEqual(supervisor.snapshot().status, "missing")
        self.assertIn("/opt/store/pos", supervisor.snapshot().message)

    def test_log_path_error_is_actionable(self):
        blocker = Path(self.temporary.name) / "not-a-directory"
        blocker.write_text("blocked", encoding="utf-8")
        supervisor = PosSupervisor(
            self.config,
            blocker / "pos.log",
            popen_factory=self.popen,
            executable_check=lambda _path: True,
        )
        self.assertFalse(supervisor.start())
        self.assertEqual(supervisor.snapshot().status, "failed")
        self.assertIn("Could not start POS", supervisor.snapshot().message)
        self.assertEqual(self.popen.calls, [])


if __name__ == "__main__":
    unittest.main()
