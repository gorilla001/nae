TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def isotime(created):
    return created.strftime(TIME_FORMAT)
