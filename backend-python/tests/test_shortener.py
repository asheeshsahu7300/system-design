import unittest
import sys
import os

# Add parent app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.encoder import encode_base62, decode_base62, generate_random_slug


class TestBase62Shortener(unittest.TestCase):
    def test_base62_encoding_decoding(self):
        test_numbers = [0, 1, 61, 62, 1000, 125301, 100000000, 3521614606207]
        for num in test_numbers:
            encoded = encode_base62(num)
            self.assertIsInstance(encoded, str)
            self.assertGreater(len(encoded), 0)
            decoded = decode_base62(encoded)
            self.assertEqual(decoded, num, f"Mismatch for {num}: encoded {encoded}, decoded {decoded}")

    def test_random_slug_length_and_uniqueness(self):
        slugs = set()
        for _ in range(100):
            s = generate_random_slug(7)
            self.assertEqual(len(s), 7)
            self.assertNotIn(s, slugs)
            slugs.add(s)

    def test_invalid_base62_character(self):
        with self.assertRaises(ValueError):
            decode_base62("invalid-dash!")


if __name__ == "__main__":
    unittest.main()
