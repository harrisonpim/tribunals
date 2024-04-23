import hashlib


def pretty_hash(input_data: dict) -> str:
    """
    Generates a neat identifier using eight unambiguous lowercase and numeric characters

    The resulting identifiers look something like this: ["2sgknw32", "gg7h2j2s", ...]

    With a set of 31 possible characters and 8 positions, this function is able to
    generate 31^8 = 852,891,037,441 unique identifiers. This should be more than enough
    for most use cases!

    :param dict input_data: the data to be hashed
    :return str: the identifier
    """
    characters = "abcdefghjkmnpqrstuvwxyz23456789"

    input_string = str(input_data)
    hash = hashlib.sha256(input_string.encode()).digest()

    output = []
    for i in range(8):
        hash_byte = hash[i]
        character_index = hash_byte % len(characters)
        output.append(characters[character_index])

    return "".join(output)
