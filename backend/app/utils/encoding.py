import base64


def decode_base64(encoded_str):
    # Convert string to bytes if necessary
    if isinstance(encoded_str, str):
        encoded_bytes = encoded_str.encode()
    else:
        encoded_bytes = encoded_str

    # Decode the base64 bytes
    decoded_bytes = base64.b64decode(encoded_bytes)

    # Convert bytes to string (if the original data was a string)
    try:
        original_str = decoded_bytes.decode()
        return original_str
    except UnicodeDecodeError:
        # Return bytes if it cannot be converted to a string (e.g., binary data)
        return decoded_bytes
