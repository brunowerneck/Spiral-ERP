def validate_name(name, min_length=3, max_length=240):
    return min_length <= len(name) <= max_length
