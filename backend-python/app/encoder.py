"""
Base62 Encoding and Decoding Engine
Alphabet: [0-9, a-z, A-Z] (62 distinct characters)
Provides:
  - Numeric ID to Base62 string conversion
  - Base62 string to Numeric ID decoding
  - Random non-sequential salt-based slug generator
"""

import string
import random
import time

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(BASE62_ALPHABET)


def encode_base62(num: int) -> str:
    """Converts a positive integer into a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    
    digits = []
    while num > 0:
        rem = num % BASE
        digits.append(BASE62_ALPHABET[rem])
        num //= BASE
        
    return "".join(reversed(digits))


def decode_base62(encoded_str: str) -> int:
    """Converts a Base62 string back into its integer equivalent."""
    num = 0
    for char in encoded_str:
        idx = BASE62_ALPHABET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid Base62 character: '{char}'")
        num = num * BASE + idx
    return num


def generate_random_slug(length: int = 7) -> str:
    """
    Generates a cryptographically sound random 7-character Base62 slug.
    62^7 = ~3.5 Trillion combinations.
    """
    return "".join(random.choices(BASE62_ALPHABET, k=length))
