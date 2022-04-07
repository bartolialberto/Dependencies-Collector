from datetime import datetime, timedelta


def compute_delta_and_stamp(dt: datetime) -> str:
    delta_in_seconds = (datetime.now() - dt).total_seconds()
    td = timedelta(seconds=delta_in_seconds)
    return str(td)

