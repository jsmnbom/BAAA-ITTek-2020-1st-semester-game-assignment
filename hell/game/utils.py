def valmap(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def blink(value, tween_in, tween_out, interval, color):
    if value > interval / 2:
        return color[:3] + (int(tween_in(valmap(value, interval / 2, interval, 0, 1)) * 255),)
    else:
        return color[:3] + (int(tween_out(valmap(value, 0, interval / 2, 1, 0)) * 255),)
