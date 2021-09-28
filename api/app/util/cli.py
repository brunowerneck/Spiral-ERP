def writeln(text: str = None, length: int = 0, fill: str = "", start: str = "", end: str = ""):
    if length < 0:
        raise AttributeError('length must be greater than or equals to zero')

    ln = start[0] if len(start) > 0 else ''

    if text is None:
        for _ in range(length):
            ln += fill[0] if len(fill) > 0 else ''
    else:
        half_length = length // 2 - (len(text) // 2)
        if half_length > 0:
            for _ in range(half_length):
                ln += fill[0] if len(fill) > 0 else ''

        ln += text

        if half_length > 0:
            iteration = half_length if half_length % 2 == 0 else half_length + 1
            for _ in range(iteration):
                ln += fill[0] if len(fill) > 0 else ''

    ln += end[0] if len(end) > 0 else ''

    print(ln)
