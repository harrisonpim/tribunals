import hashlib
import re
from typing import Any


class Identifier(str):
    """
    An identifier that uses eight unambiguous lowercase and numeric characters.

    Identifiers look something like: ["2sgknw32", "gg7h2j2s", ...]
    With 31 possible characters and 8 positions, this can generate
    31^8 = 852,891,037,441 unique ids.
    """

    # Excludes "i", "l", "1", "o", "0" to minimize ambiguity
    characters = "abcdefghjkmnpqrstuvwxyz23456789"
    regex = rf"^[{characters}]{8}$"

    @classmethod
    def _validate(cls, value: str, field: Any = None) -> str:
        """Validate that the identifier matches the expected pattern"""
        if not re.match(cls.regex, value):
            raise ValueError(
                f"{value} is not a valid identifier. "
                f"Must be 8 characters long using only {cls.characters}"
            )
        return value

    @classmethod
    def __get_validators__(cls):
        """Return a generator of validators"""
        yield cls._validate

    def __new__(cls, value: str) -> "Identifier":
        """Create a new Identifier instance after validation"""
        validated_value = cls._validate(value)
        return str.__new__(cls, validated_value)

    @classmethod
    def generate(cls, *args) -> "Identifier":
        """Generate a deterministic identifier from the input arguments"""
        input_string = "".join([str(arg) for arg in args])
        hashed_data = hashlib.sha256(input_string.encode()).digest()
        identifier = "".join(
            cls.characters[b % len(cls.characters)] for b in hashed_data[:8]
        )
        return cls(identifier)
