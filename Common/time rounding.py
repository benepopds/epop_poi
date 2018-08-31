#https://gist.github.com/comargo/16c049f14381f7789c8a1de239ad133e

from datetime import timedelta
def ceil_dt(dt, res):
    # how many secs have passed this day
    nsecs = dt.hour*3600 + dt.minute*60 + dt.second + dt.microsecond*1e-6
    delta = res.seconds - nsecs % res.seconds
    if delta == res.seconds:
        delta = 0
    return dt + datetime.timedelta(seconds=delta)

def floor_dt(dt, res):
    # how many secs have passed this day
    nsecs = dt.hour*3600 + dt.minute*60 + dt.second + dt.microsecond*1e-6
    delta = nsecs % res.seconds
    return dt - datetime.timedelta(seconds=delta)