import json
from pathlib import Path
import tempfile
import unittest

from rtylr_shell.config import ConfigError, ConfigStore, Paths, StateStore, validate_config


class ConfigStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.paths = Paths(
            default_config=root / "default.json",
            runtime_config=root / "runtime.json",
            state_file=root / "state.json",
            application_log=root / "application.log",
            device_id=root / "device-id",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_runtime_config_deep_merges_defaults(self):
        self.paths.default_config.write_text(
            json.dumps(
                {"brand": {"name": "Company OS"}, "application": {"name": "Default app"}}
            ),
            encoding="utf-8",
        )
        self.paths.runtime_config.write_text(
            json.dumps({"application": {"name": "Business workspace", "auto_start": False}}),
            encoding="utf-8",
        )
        config = ConfigStore(self.paths).load()
        self.assertEqual(config["brand"]["name"], "Company OS")
        self.assertEqual(config["brand"]["wordmark"], "RTYLR")
        self.assertEqual(config["application"]["name"], "Business workspace")
        self.assertFalse(config["application"]["auto_start"])
        self.assertEqual(config["application"]["restart"]["max_attempts"], 5)

    def test_legacy_pos_config_is_migrated(self):
        self.paths.runtime_config.write_text(
            json.dumps({"pos": {"name": "Legacy checkout", "auto_start": False}}),
            encoding="utf-8",
        )
        config = ConfigStore(self.paths).load()
        self.assertNotIn("pos", config)
        self.assertEqual(config["application"]["name"], "Legacy checkout")
        self.assertFalse(config["application"]["auto_start"])

    def test_save_round_trips_valid_config(self):
        store = ConfigStore(self.paths)
        config = store.load()
        config["application"]["command"] = ["/opt/company/workspace", "--kiosk"]
        config["application"]["working_directory"] = "/opt/company"
        store.save(config)
        self.assertEqual(store.load()["application"]["command"][1], "--kiosk")
        self.assertNotIn("pos", json.loads(self.paths.runtime_config.read_text(encoding="utf-8")))

    def test_rejects_relative_executable(self):
        config = ConfigStore(self.paths).load()
        config["application"]["command"] = ["business-app"]
        with self.assertRaises(ConfigError):
            validate_config(config)

    def test_state_setup_flag_is_strict_boolean(self):
        state = StateStore(self.paths)
        state.load()
        state.set("setup_complete", "yes")
        self.assertFalse(state.setup_complete)
        state.set("setup_complete", True)
        state.save()
        reloaded = StateStore(self.paths)
        reloaded.load()
        self.assertTrue(reloaded.setup_complete)


if __name__ == "__main__":
    unittest.main()
