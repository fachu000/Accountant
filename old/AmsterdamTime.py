
#  Conversion from Amsterdam time (CET in winter and CST in summer) to
#  UTC and vice versa
#
# Example:
# from AmsterdamTime import AmsterdamTime, UTC
# from datetime import datetime,timedelta,time
#
# dt = datetime(year=2017, month=10, day=30, hour=10, minute=30,tzinfo=AmsterdamTime())
# dtutc = dt.astimezone(tz = UTC())
# print(dtutc.time())



from datetime import datetime, tzinfo, timedelta

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


class AmsterdamTime(tzinfo):
    """Amsterdam time is UTC+1 in winter and UTC+2 in summer"""
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)

    def dst(self, dt):
        # changes are the last sunday of the month
        dston = first_sunday_on_or_after(datetime(year=dt.year, month=3, day=25))
        dstoff = first_sunday_on_or_after(datetime(year=dt.year, month=10, day=25))
        if dston <= dt.replace(tzinfo=None) < dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)
