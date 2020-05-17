def valmap(value, istart, istop, ostart, ostop):
    """Maps a value in the range istart,istop to ostart,ostop."""
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def blink(value, tween_in, tween_out, interval, color):
    """Output color with blinking alpha value.

    value should be between 0 and interval."""
    if value > interval / 2:
        # Take RGB (not A) from color and add our tweened A value
        # The if above means value is from interval/2 to interval
        # Since it's tween_IN we make that from 0 to 1
        return color[:3] + (int(tween_in(valmap(value, interval / 2, interval, 0, 1)) * 255),)
    else:
        # Take RGB (not A) from color and add our tweened A value
        # The if above means value is from 0 to interval/2
        # Since it's tween_OUT we make that from 1 to 0
        return color[:3] + (int(tween_out(valmap(value, 0, interval / 2, 1, 0)) * 255),)
