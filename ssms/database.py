from ssms import app

_session = None


def session():
    global _session
    if not _session:
        _session = app.Session()
    return _session
