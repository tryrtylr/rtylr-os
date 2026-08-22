from pathlib import Path
import tempfile
import unittest

from rtylr_shell.actions import read_log_tail, support_code


class ActionTests(unittest.TestCase):
    def test_support_code_is_stable_and_short(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "device-id"
            path.write_text("terminal-123\n", encoding="utf-8")
            first = support_code(path)
            second = support_code(path)
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9A-F]{4}-[0-9A-F]{4}$")

    def test_log_tail_is_bounded(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "pos.log"
            path.write_text("\n".join(str(index) for index in range(20)), encoding="utf-8")
            tail = read_log_tail(path, maximum_lines=3)
        self.assertEqual(tail.splitlines(), ["17", "18", "19"])


if __name__ == "__main__":
    unittest.main()
