import unittest

from rtylr_shell.security import hash_pin, valid_pin, verify_pin


class PinTests(unittest.TestCase):
    def test_pin_validation(self):
        self.assertTrue(valid_pin("1234"))
        self.assertTrue(valid_pin("12345678"))
        self.assertFalse(valid_pin("123"))
        self.assertFalse(valid_pin("123456789"))
        self.assertFalse(valid_pin("12a4"))
        self.assertFalse(valid_pin("١٢٣٤"))

    def test_hash_and_verify(self):
        record = hash_pin("4826", salt=b"0123456789abcdef", iterations=1_000)
        self.assertTrue(verify_pin("4826", record))
        self.assertFalse(verify_pin("4827", record))
        self.assertNotIn("4826", str(record))

    def test_malformed_record_fails_closed(self):
        self.assertFalse(verify_pin("1234", "not-a-record"))
        self.assertFalse(verify_pin("1234", {"algorithm": "unknown"}))
        self.assertFalse(verify_pin("1234", {"algorithm": "pbkdf2-sha256"}))
        record = hash_pin("1234", salt=b"0123456789abcdef", iterations=1_000)
        record["iterations"] = -1
        self.assertFalse(verify_pin("1234", record))
        record["iterations"] = 9_999_999_999
        self.assertFalse(verify_pin("1234", record))


if __name__ == "__main__":
    unittest.main()
