from pytz import timezone
from datetime import datetime


def getds():
    est = timezone('US/Eastern')
    local = est.localize(datetime.now())
    fmt = '%Y-%m-%d %H:%M:%S %z'
    return local.strftime(fmt)
