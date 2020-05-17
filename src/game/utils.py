def valmap(value, istart, istop, ostart, ostop):
    """Maps a value in the range istart,istop to ostart,ostop."""
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def blink(value, tween_in, tween_out, interval, color):
    """Output color with blinking alpha value.

    value should be between 0 and interval."""
    if value > interval / 2:
        return color[:3] + (int(tween_in(valmap(value, interval / 2, interval, 0, 1)) * 255),)
    else:
        return color[:3] + (int(tween_out(valmap(value, 0, interval / 2, 1, 0)) * 255),)
