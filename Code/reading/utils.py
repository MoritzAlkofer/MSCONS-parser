    
def split_with_release(string, separators, separator):
    """Split string by separator, ignoring escaped separators"""
    escape_seq = separators['release_character'] + separator
    temp_placeholder = '\x00'  # Use null character as temporary placeholder
    
    # Replace escaped separators with placeholder
    protected = string.replace(escape_seq, temp_placeholder)
    # Split on unescaped separators
    parts = protected.split(separator)
    # Restore escaped separators
    return [part.replace(temp_placeholder, separator) for part in parts]