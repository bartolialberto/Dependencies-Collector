from datetime import datetime


def compute_delta_and_print(dt: datetime) -> str:
    delta_in_seconds = (datetime.now() - dt).total_seconds()
    if delta_in_seconds >= (60*60):
        return f"{(delta_in_seconds / (60*60)):.2f} hrs"
    elif delta_in_seconds >= 60:
        return f"{(delta_in_seconds / 60):.2f} min"
    else:
        return f"{delta_in_seconds:.2f} sec"
