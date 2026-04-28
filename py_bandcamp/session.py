import requests

SESSION = requests.Session()


def set_session(session):
    """Replace the global HTTP session (e.g. to inject auth headers or a mock)."""
    global SESSION
    SESSION = session
