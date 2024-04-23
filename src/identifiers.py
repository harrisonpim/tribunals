def pretty_hash(input_data: dict) -> str:
    """
    Generates a neat identifier using eight unambiguous lowercase and numeric characters

    With a set of 31 possible characters and 8 positions, this function is able to
    generate 31^8 = 852,891,037,441 unique identifiers. This should be more than enough
    for most use cases!

    :param dict input_data: the data to be hashed
    :return str: the identifier
    """
    characters = "abcdefghjkmnpqrstuvwxyz23456789"
    input_str = str(input_data)
    input_bytes = input_str.encode()
    output = []
    for i in range(8):
        byte = input_bytes[i] if i < len(input_bytes) else 0
        output.append(characters[byte % len(characters)])
    return "".join(output)
