from datetime import datetime, timedelta


def compute_delta_and_stamp(dt: datetime) -> str:
    """
    Static method that takes a datetime object and returns a string representation of the difference between time
    expressed in the parameter and right now.

    :param dt: A particular instance in time.
    :type dt: datetime
    :return: A string representation (HH:mm:ss:us)
    :rtype: str
    """
    delta_in_seconds = (datetime.now() - dt).total_seconds()
    td = timedelta(seconds=delta_in_seconds)
    return str(td)

